#!/usr/bin/env node
/**
 * submit-wfh-leave.js
 *
 * Automates WFH leave submission to the DHL MyPortalPlus HR portal.
 *
 * Usage:
 *   node submit-wfh-leave.js --month=June --days=Mon,Tue,Wed
 *   node submit-wfh-leave.js --month=July --days=Mon,Wed --dry-run
 *
 *   # Pass explicit dates (agent uses this when the user limits to specific weeks)
 *   node submit-wfh-leave.js --dates=2026-06-01,2026-06-02,2026-06-03,2026-06-04
 *   node submit-wfh-leave.js --dates=2026-06-01,2026-06-04 --dry-run
 *
 * Prerequisites:
 *   npm install playwright
 *   npx playwright install chromium
 */

const { chromium } = require('playwright');

// ---- Portal constants (from HAR analysis) ------------------------------------
const PORTAL_URL  = 'https://myportalplus.prg-dc.dhl.com:8406/sap/bc/ui2/flp?sap-client=100&appState=lean';
const ODATA_BASE  = 'https://myportalplus.prg-dc.dhl.com:8406/sap/opu/odata/sap/YFLEXUI_LEAVE_REQUEST_SRV';
const SSO_SIGNAL  = '/sap/opu/odata/UI2/INTEROP/PersContainers';

const WFH_ABSENCE_TYPE_ID = '00080410';  // "Working from home"
const WHOLE_DAY_TYPE_ID   = '00081';     // "Whole day"
const HOME_ADDR_SEQNR     = '001';       // Home office address sequence
const HOME_ADDR_ID        = 'YZ02';      // "Home office address"

const SSO_TIMEOUT_MS      = 3 * 60 * 1000;   // 3 minutes for SSO login
const SUBMIT_DELAY_MS     = 800;              // delay between submissions

// ---- Argument parsing --------------------------------------------------------
const rawArgs = process.argv.slice(2);
const args = Object.fromEntries(
  rawArgs.filter(a => a.startsWith('--')).map(a => {
    const [k, v] = a.slice(2).split('=');
    return [k, v];
  })
);
const dryRun = rawArgs.includes('--dry-run');

// ---- Date helpers ------------------------------------------------------------
const DAY_MAP = { sun: 0, mon: 1, tue: 2, wed: 3, thu: 4, fri: 5, sat: 6 };

function parseWfhDays(daysArg) {
  return daysArg.split(',').map(d => {
    const key = d.trim().toLowerCase().slice(0, 3);
    if (DAY_MAP[key] === undefined) throw new Error(`Unknown day: ${d.trim()}`);
    return DAY_MAP[key];
  });
}

function getWfhDates(monthName, targetDayNumbers) {
  const now   = new Date();
  let year    = now.getFullYear();
  const trial = new Date(`${monthName} 1, ${year}`);
  if (isNaN(trial)) throw new Error(`Unknown month: ${monthName}`);
  // If the month is already past this year, use next year
  if (trial.getMonth() < now.getMonth()) year++;
  const dates = [];
  const d = new Date(year, trial.getMonth(), 1);
  while (d.getMonth() === trial.getMonth()) {
    if (targetDayNumbers.includes(d.getDay())) dates.push(new Date(d));
    d.setDate(d.getDate() + 1);
  }
  return dates;
}

// SAP OData date: UTC midnight in milliseconds, formatted as /Date(ms)/
function toSapDate(date) {
  const ms = Date.UTC(date.getFullYear(), date.getMonth(), date.getDate());
  return `/Date(${ms})/`;
}

function formatDate(date) {
  return date.toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric' });
}

// Group sorted dates into consecutive runs (diff of exactly 1 calendar day = same group)
function groupConsecutiveDates(dates) {
  if (dates.length === 0) return [];
  const groups = [];
  let current = [dates[0]];
  for (let i = 1; i < dates.length; i++) {
    const diffDays = (dates[i] - dates[i - 1]) / 86400000;
    if (diffDays === 1) {
      current.push(dates[i]);
    } else {
      groups.push(current);
      current = [dates[i]];
    }
  }
  groups.push(current);
  return groups;
}

// ---- OData submission (runs inside browser via page.evaluate) ----------------
async function submitDateRange(page, startDate, endDate) {
  const sapStart = toSapDate(startDate);
  const sapEnd   = toSapDate(endDate);
  return page.evaluate(async ({ odataBase, absenceTypeId, dayTypeId, addrSeqnr, addrId, sapStart, sapEnd }) => {
    const rand = () => Math.random().toString(36).slice(2, 10);

    // Step 1: fetch CSRF token (HEAD request matches portal behaviour)
    const tokenResp = await fetch(`${odataBase}/?sap-client=100`, {
      method: 'HEAD', credentials: 'include',
      headers: { 'x-csrf-token': 'Fetch', 'Accept': 'application/json',
                 'DataServiceVersion': '2.0', 'MaxDataServiceVersion': '2.0' }
    });
    const csrfToken = tokenResp.headers.get('x-csrf-token');
    if (!csrfToken || csrfToken === 'Required') throw new Error('No CSRF token returned');

    const outerHeaders = {
      'DataServiceVersion':    '2.0',
      'MaxDataServiceVersion': '2.0',
      'x-csrf-token':          csrfToken,
      'X-Requested-With':      'XMLHttpRequest',
      'Accept':                'multipart/mixed',
      'Accept-Language':       'en',
      'sap-contextid-accept':  'header',
      'sap-cancel-on-close':   'false'
    };

    // Step 2: create draft leave request
    const batch1 = `batch_${rand()}`;
    const cset1  = `changeset_${rand()}`;
    const cid1   = `id-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
    const body1  = [
      `--${batch1}`,
      `Content-Type: multipart/mixed; boundary=${cset1}`, '',
      `--${cset1}`,
      'Content-Type: application/http',
      'Content-Transfer-Encoding: binary', '',
      'POST LeaveRequests?sap-client=100 HTTP/1.1',
      'sap-contextid-accept: header',
      'Accept: application/json', 'Accept-Language: en',
      'DataServiceVersion: 2.0', 'MaxDataServiceVersion: 2.0',
      'X-Requested-With: XMLHttpRequest',
      `x-csrf-token: ${csrfToken}`,
      'Content-Type: application/json',
      `Content-ID: ${cid1}`,
      'Content-Length: 17', '',
      '{"Statustype":""}',
      `--${cset1}--`, '',
      `--${batch1}--`
    ].join('\r\n');

    const createResp = await fetch(`${odataBase}/$batch?sap-client=100`, {
      method: 'POST', credentials: 'include',
      headers: { ...outerHeaders, 'Content-Type': `multipart/mixed;boundary=${batch1}` },
      body: body1
    });
    const createText = await createResp.text();
    // Draft IDs start with 0008D; match only those to avoid picking up a GET URL in the same response
    const leaveIdMatch = createText.match(/LeaveRequests\('(0008D[^']+)'\)/);
    if (!leaveIdMatch) throw new Error('Draft creation failed — could not extract LeaveId from: ' + createText.slice(0, 300));
    const leaveId = leaveIdMatch[1];

    // Step 3: MERGE draft with date/type/address, then GET to confirm + read AbsenceUsedHours
    const batch2 = `batch_${rand()}`;
    const cset2  = `changeset_${rand()}`;
    const cid2   = `id-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
    const mergePayload = JSON.stringify({
      Absencetypeid: absenceTypeId,
      Startdate:     sapStart,
      Enddate:       sapEnd,
      Daytypeid:     dayTypeId,
      Addressid:     addrId,
      Addressseqnr:  addrSeqnr,
      Note:          ''
    });
    const body2 = [
      `--${batch2}`,
      `Content-Type: multipart/mixed; boundary=${cset2}`, '',
      `--${cset2}`,
      'Content-Type: application/http',
      'Content-Transfer-Encoding: binary', '',
      `MERGE LeaveRequests('${leaveId}')?sap-client=100 HTTP/1.1`,
      'sap-contextid-accept: header',
      'Accept: application/json', 'Accept-Language: en',
      'DataServiceVersion: 2.0', 'MaxDataServiceVersion: 2.0',
      'X-Requested-With: XMLHttpRequest',
      `x-csrf-token: ${csrfToken}`,
      'Content-Type: application/json',
      `Content-ID: ${cid2}`,
      `Content-Length: ${mergePayload.length}`, '',
      mergePayload,
      `--${cset2}--`, '',
      `--${batch2}`,
      'Content-Type: application/http',
      'Content-Transfer-Encoding: binary', '',
      `GET LeaveRequests('${leaveId}')?sap-client=100 HTTP/1.1`,
      'sap-cancel-on-close: true',
      'sap-contextid-accept: header',
      'Accept: application/json', 'Accept-Language: en',
      'DataServiceVersion: 2.0', 'MaxDataServiceVersion: 2.0',
      'X-Requested-With: XMLHttpRequest',
      `x-csrf-token: ${csrfToken}`, '', '',
      `--${batch2}--`
    ].join('\r\n');

    const mergeResp = await fetch(`${odataBase}/$batch?sap-client=100`, {
      method: 'POST', credentials: 'include',
      headers: { ...outerHeaders, 'Content-Type': `multipart/mixed;boundary=${batch2}` },
      body: body2
    });
    const mergeText = await mergeResp.text();

    if (!mergeText.includes('204 No Content')) {
      throw new Error('MERGE step did not return 204 No Content: ' + mergeText.slice(0, 300));
    }

    // Extract hours from the GET LeaveRequests response (needed by LeaveRequestSend)
    const hoursMatch = mergeText.match(/"Absenceusedhours":"([^"]+)"/);
    const absenceUsedHours = hoursMatch ? hoursMatch[1] : '8.00';

    // Step 4: submit via LeaveRequestSend — this is what moves the draft to "Not processed"
    const batch3 = `batch_${rand()}`;
    const sendQs  = `sap-client=100&LeaveID='${leaveId}'&Note=''&Pernr=''&AbsenceUsedHours='${absenceUsedHours}'&SubPernr=''`;
    const body3  = [
      `--${batch3}`,
      'Content-Type: application/http',
      'Content-Transfer-Encoding: binary', '',
      `GET LeaveRequestSend?${sendQs} HTTP/1.1`,
      'sap-contextid-accept: header',
      'Accept: application/json', 'Accept-Language: en',
      'DataServiceVersion: 2.0', 'MaxDataServiceVersion: 2.0',
      'X-Requested-With: XMLHttpRequest',
      `x-csrf-token: ${csrfToken}`, '', '',
      `--${batch3}--`
    ].join('\r\n');

    const sendResp = await fetch(`${odataBase}/$batch?sap-client=100`, {
      method: 'POST', credentials: 'include',
      headers: { ...outerHeaders, 'Content-Type': `multipart/mixed;boundary=${batch3}` },
      body: body3
    });
    const sendText = await sendResp.text();

    if (!sendText.includes('200 OK')) {
      throw new Error('LeaveRequestSend did not return 200 OK: ' + sendText.slice(0, 300));
    }

    return { leaveId };
  }, { odataBase: ODATA_BASE, absenceTypeId: WFH_ABSENCE_TYPE_ID, dayTypeId: WHOLE_DAY_TYPE_ID, addrSeqnr: HOME_ADDR_SEQNR, addrId: HOME_ADDR_ID, sapStart, sapEnd });
}

// ---- Main -------------------------------------------------------------------
async function main() {
  if (!args.dates && (!args.month || !args.days)) {
    console.error('Usage: node submit-wfh-leave.js --month=<Month> --days=<Mon,Tue,Wed>');
    console.error('       node submit-wfh-leave.js --dates=2026-06-01,2026-06-02,...');
    console.error('       Add --dry-run to preview dates without submitting.');
    process.exit(1);
  }

  let dates;
  let planLabel;

  if (args.dates) {
    // Explicit date list — agent already filtered to exactly the dates the user approved
    dates = args.dates.split(',').map(s => {
      const d = new Date(s.trim() + 'T00:00:00');
      if (isNaN(d)) { console.error(`Invalid date: ${s.trim()}`); process.exit(1); }
      return d;
    });
    planLabel = `${dates.length} selected date${dates.length !== 1 ? 's' : ''}`;
  } else {
    let targetDayNumbers;
    try {
      targetDayNumbers = parseWfhDays(args.days);
    } catch (e) {
      console.error(e.message);
      process.exit(1);
    }
    try {
      dates = getWfhDates(args.month, targetDayNumbers);
    } catch (e) {
      console.error(e.message);
      process.exit(1);
    }
    planLabel = `${args.month} (${args.days.split(',').map(d => d.trim()).join(', ')})`;
  }

  if (dates.length === 0) {
    console.log('No dates to submit.');
    process.exit(0);
  }

  const groups = groupConsecutiveDates(dates);
  console.log('');
  console.log(`WFH leave plan — ${planLabel}`);
  console.log('='.repeat(55));
  groups.forEach((g, i) => {
    const start = g[0];
    const end   = g[g.length - 1];
    const label = g.length === 1
      ? formatDate(start)
      : `${formatDate(start)}  ->  ${formatDate(end)}`;
    console.log(`  ${String(i + 1).padStart(2)}. ${label}  (${g.length} day${g.length > 1 ? 's' : ''})`);
  });
  console.log(`${''.padEnd(55, '-')}`);
  console.log(`  Requests: ${groups.length}   Days: ${dates.length}`);
  console.log('');

  if (dryRun) {
    console.log('Dry run — no submissions made.');
    return;
  }

  // Launch browser
  let browser;
  try {
    browser = await chromium.launch({ headless: false, channel: 'chrome' });
  } catch {
    // Fall back to bundled Chromium if Chrome is not installed
    browser = await chromium.launch({ headless: false });
  }

  const context = await browser.newContext();
  const page    = await context.newPage();

  // Detect SSO completion via PersContainers response
  let ssoComplete = false;
  page.on('response', resp => {
    if (resp.url().includes(SSO_SIGNAL) && resp.status() === 200) ssoComplete = true;
  });

  await page.goto(PORTAL_URL);
  console.log('Browser opened. Complete your SSO login — the script continues automatically.');
  console.log(`(Waiting up to ${SSO_TIMEOUT_MS / 60000} minutes...)`);
  console.log('');

  const ssoStart = Date.now();
  while (!ssoComplete && Date.now() - ssoStart < SSO_TIMEOUT_MS) {
    await page.waitForTimeout(1000);
  }

  if (!ssoComplete) {
    console.error('SSO timeout — no PersContainers signal received. Please try again.');
    await browser.close();
    process.exit(1);
  }

  console.log('SSO complete. Starting submissions...');
  console.log('');

  // Extra wait for the app shell to fully initialise
  await page.waitForTimeout(3000);

  const results = [];
  for (const group of groups) {
    const start = group[0];
    const end   = group[group.length - 1];
    const label = group.length === 1
      ? formatDate(start)
      : `${formatDate(start)} -> ${formatDate(end)}`;
    process.stdout.write(`  Submitting ${label}... `);
    try {
      const { leaveId } = await submitDateRange(page, start, end);
      console.log(`OK  (${leaveId})`);
      results.push({ label, status: 'submitted', leaveId, days: group.length });
    } catch (err) {
      console.log(`FAILED: ${err.message}`);
      results.push({ label, status: 'failed', error: err.message, days: group.length });
    }
    await page.waitForTimeout(SUBMIT_DELAY_MS);
  }

  // Summary
  const succeeded = results.filter(r => r.status === 'submitted');
  const failed    = results.filter(r => r.status === 'failed');
  const daysOk    = succeeded.reduce((n, r) => n + r.days, 0);
  console.log('');
  console.log('='.repeat(55));
  console.log(`  Requests submitted : ${succeeded.length} of ${groups.length}`);
  console.log(`  Days covered       : ${daysOk} of ${dates.length}`);
  console.log(`  Failed requests    : ${failed.length}`);
  console.log('='.repeat(55));

  if (failed.length > 0) {
    console.log('');
    console.log('Failed requests (submit manually in the portal):');
    failed.forEach(r => console.log(`  - ${r.label}: ${r.error}`));
  } else {
    console.log('');
    console.log('All done. Check "My Leave Requests" in the portal to confirm.');
  }

  await browser.close();
}

main().catch(err => {
  console.error('Unexpected error:', err.message);
  process.exit(1);
});
