// DHL Mobile UI Kit — screens
const { useState: useStateM } = React;

const PARCELS = [
  { sender: "Apple Online Store",      tn: "1234 5678 9012", status: "out",       eta: "Today, by 18:00",   service: "Express",   accent: true },
  { sender: "Zalando.de",              tn: "JD0156 7890 12", status: "transit",   eta: "Tomorrow, by 17:00", service: "Parcel" },
  { sender: "IKEA Deutschland",        tn: "3456 7890 1234", status: "scheduled", eta: "Thu, 10:00–12:00",   service: "Parcel" },
  { sender: "Decathlon Lyon",          tn: "JD0167 4321 09", status: "delivered", eta: "Yesterday, 16:42",   service: "Express" },
  { sender: "Outgoing — Marc Bernard", tn: "5544 3322 1100", status: "pickup",    eta: "Drop at Service Point", service: "Parcel" }
];

const EVENTS = [
  { label: "Out for delivery",  location: "Lyon · Courier 7184",  when: "Today · 09:42", current: true, done: true },
  { label: "Arrived at facility", location: "Lyon delivery hub", when: "Today · 06:55", done: true },
  { label: "Customs cleared",   location: "Lyon Saint-Exupéry",  when: "Wed · 09:18", done: true },
  { label: "Departed EU Hub",   location: "Leipzig, Germany",    when: "Tue · 22:30", done: true },
  { label: "Picked up",         location: "Leipzig, Germany",    when: "Mon · 14:02", done: true }
];

/* Screen 1: Parcels (home) */
function MParcelsScreen() {
  return (
    <div style={{ background: "#fff", height: "100%", display: "flex", flexDirection: "column", fontFamily: M_FONT }}>
      <MobileHeader title="Parcels" subtitle="5 parcels, 1 out today." />
      <div style={{ background: "#fff", padding: "12px 18px 8px", display: "flex", gap: 8, overflowX: "auto", borderBottom: `1px solid ${M_GRAY150}` }}>
        {[
          { l: "All", n: 5, active: true },
          { l: "Incoming", n: 4 },
          { l: "Outgoing", n: 1 },
          { l: "Delivered", n: 12 }
        ].map((f, i) => (
          <button key={i} style={{
            border: f.active ? `1.5px solid #000` : `1.5px solid ${M_GRAY200}`,
            background: f.active ? "#000" : "#fff",
            color: f.active ? "#fff" : "#000",
            borderRadius: 999, padding: "6px 14px",
            font: `700 12px/1 ${M_FONT}`,
            display: "flex", alignItems: "center", gap: 5, cursor: "pointer"
          }}>
            {f.l} <span style={{ opacity: .7, fontSize: 11 }}>{f.n}</span>
          </button>
        ))}
      </div>
      <div style={{ flex: 1, overflow: "auto" }}>
        {PARCELS.map((p, i) => <ParcelRow key={i} {...p} />)}
      </div>
      <BottomNav current="parcels" />
    </div>
  );
}

/* Screen 2: Detail / Tracking */
function MDetailScreen() {
  return (
    <div style={{ background: "#fff", height: "100%", display: "flex", flexDirection: "column", fontFamily: M_FONT, position: "relative" }}>
      {/* Hero band */}
      <div style={{ background: M_YELLOW, padding: "14px 18px 22px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", height: 28 }}>
          <MIcon name="chevron-left" size={22} color="#000" stroke={1.75} />
          <div style={{ fontSize: 13, fontWeight: 700 }}>Parcel</div>
          <MIcon name="more-horizontal" size={22} color="#000" stroke={1.75} />
        </div>
        <div style={{ marginTop: 18 }}>
          <MLabel>Express Worldwide</MLabel>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "rgba(0,0,0,.65)", marginTop: 6 }}>1234 5678 9012</div>
          <div style={{ fontFamily: "var(--font-display)", fontWeight: 900, fontSize: 38, lineHeight: 1.05, marginTop: 8 }}>Out for<br/>delivery.</div>
          <div style={{ fontSize: 13, color: "rgba(0,0,0,.78)", marginTop: 6 }}>Expected <strong>today, by 18:00</strong>.</div>
        </div>
      </div>

      {/* Body */}
      <div style={{ flex: 1, overflow: "auto", padding: "18px 18px 100px" }}>
        {/* Sender / recipient */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 32px 1fr", alignItems: "center", padding: "12px 0 18px", borderBottom: `1px solid ${M_GRAY150}` }}>
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: M_GRAY600 }}>From</div>
            <div style={{ fontSize: 14, fontWeight: 700, marginTop: 3 }}>Leipzig</div>
            <div style={{ fontSize: 11, color: M_GRAY600 }}>Germany</div>
          </div>
          <MIcon name="arrow-right" size={20} color={M_RED} stroke={2} />
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: M_GRAY600 }}>To</div>
            <div style={{ fontSize: 14, fontWeight: 700, marginTop: 3 }}>Lyon</div>
            <div style={{ fontSize: 11, color: M_GRAY600 }}>France</div>
          </div>
        </div>

        {/* Action row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, padding: "14px 0 18px", borderBottom: `1px solid ${M_GRAY150}` }}>
          <MButton variant="primary" icon="calendar" fullWidth size="sm">Schedule</MButton>
          <MButton variant="ghost" icon="map-pin" fullWidth size="sm">Send to locker</MButton>
        </div>

        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase", color: M_GRAY600, margin: "22px 0 14px" }}>Event history</div>
        <VTimeline events={EVENTS} />
      </div>
    </div>
  );
}

/* Screen 3: Schedule delivery */
function MScheduleScreen() {
  const [opt, setOpt] = useStateM("home-evening");
  const [day, setDay] = useStateM(1);
  const days = [
    { l: "Today",    d: "May 20", disabled: true },
    { l: "Tomorrow", d: "May 21" },
    { l: "Thu",      d: "May 22" },
    { l: "Fri",      d: "May 23" }
  ];
  return (
    <div style={{ background: "#fff", height: "100%", display: "flex", flexDirection: "column", fontFamily: M_FONT, position: "relative" }}>
      <div style={{ background: M_YELLOW, padding: "14px 18px 18px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", height: 28 }}>
          <MIcon name="x" size={22} color="#000" stroke={1.75} />
          <div style={{ fontSize: 13, fontWeight: 700 }}>Schedule delivery</div>
          <div style={{ width: 22 }} />
        </div>
        <div style={{ fontFamily: "var(--font-display)", fontWeight: 900, fontSize: 30, lineHeight: 1.05, marginTop: 16 }}>Pick a day<br/>and a place.</div>
      </div>

      <div style={{ flex: 1, overflow: "auto", padding: "18px 18px 110px" }}>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: M_GRAY600, marginBottom: 10 }}>Choose a day</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8, marginBottom: 22 }}>
          {days.map((d, i) => {
            const active = day === i;
            return (
              <button key={i} disabled={d.disabled} onClick={() => setDay(i)} style={{
                border: `1.5px solid ${active ? M_RED : M_GRAY200}`,
                background: active ? "#FFF5CC" : "#fff",
                opacity: d.disabled ? .35 : 1,
                borderRadius: 6, padding: "10px 0",
                fontFamily: M_FONT, cursor: d.disabled ? "not-allowed" : "pointer",
                display: "flex", flexDirection: "column", gap: 2
              }}>
                <span style={{ fontSize: 11, color: M_GRAY600, fontWeight: 700 }}>{d.l}</span>
                <span style={{ fontSize: 14, fontWeight: 700 }}>{d.d}</span>
              </button>
            );
          })}
        </div>

        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: M_GRAY600, marginBottom: 10 }}>Where</div>
        <ScheduleOption icon="home"      title="Home address"      sub="Rue Mercière 24, Lyon · 8:00–12:00"   value="home-morning"  selectedValue={opt} onClick={setOpt} />
        <ScheduleOption icon="home"      title="Home address"      sub="Rue Mercière 24, Lyon · 17:00–20:00"  value="home-evening"  selectedValue={opt} onClick={setOpt} />
        <ScheduleOption icon="map-pin"   title="Service Point"     sub="DHL Bellecour, 0.4 km away"           value="sp"            selectedValue={opt} onClick={setOpt} />
        <ScheduleOption icon="lock"      title="Parcel locker"     sub="Locker Part-Dieu · 24/7 access"       value="locker"        selectedValue={opt} onClick={setOpt} />
        <ScheduleOption icon="users"     title="Neighbour"         sub="Add their name & flat"                value="neigh"         selectedValue={opt} onClick={setOpt} />
      </div>

      <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, background: "#fff", borderTop: `1px solid ${M_GRAY150}`, padding: "14px 18px 28px" }}>
        <MButton variant="primary" fullWidth size="lg" iconRight="arrow-right">Confirm change</MButton>
      </div>
    </div>
  );
}

/* Screen 4: Locker pickup */
function MLockerScreen() {
  return (
    <div style={{ background: "#fff", height: "100%", display: "flex", flexDirection: "column", fontFamily: M_FONT, position: "relative" }}>
      <div style={{ background: "#000", padding: "14px 18px 18px", color: "#fff" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", height: 28 }}>
          <MIcon name="chevron-left" size={22} color="#fff" stroke={1.75} />
          <div style={{ fontSize: 13, fontWeight: 700 }}>Locker pickup</div>
          <MIcon name="share" size={20} color="#fff" stroke={1.75} />
        </div>
        <div style={{ marginTop: 14 }}>
          <span style={{ display: "inline-block", padding: "3px 8px", background: M_YELLOW, color: "#000", borderRadius: 2, font: `700 9px/1.3 ${M_FONT}`, letterSpacing: ".06em", textTransform: "uppercase" }}>Ready to collect</span>
          <div style={{ fontFamily: "var(--font-display)", fontWeight: 900, fontSize: 32, lineHeight: 1, marginTop: 12 }}>
            Pick it up<br/>
            <span style={{ color: M_YELLOW }}>within 7 days.</span>
          </div>
        </div>
      </div>

      <div style={{ flex: 1, overflow: "auto" }}>
        <QRPanel code="84 21 09 77" locker="Locker Part-Dieu" addr="Gare Part-Dieu, 69003 Lyon · 24/7" />

        <div style={{ padding: "18px 18px 80px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 18 }}>
            <MButton variant="ghost" icon="navigation" fullWidth size="sm">Directions</MButton>
            <MButton variant="ghost" icon="copy" fullWidth size="sm">Copy code</MButton>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 0, border: `1px solid ${M_GRAY200}`, borderRadius: 6, overflow: "hidden" }}>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "12px 14px", borderBottom: `1px solid ${M_GRAY150}` }}>
              <span style={{ fontSize: 12, color: M_GRAY600 }}>Tracking number</span>
              <span style={{ fontSize: 12, fontFamily: "var(--font-mono)", fontWeight: 700 }}>1234 5678 9012</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "12px 14px", borderBottom: `1px solid ${M_GRAY150}` }}>
              <span style={{ fontSize: 12, color: M_GRAY600 }}>Compartment</span>
              <span style={{ fontSize: 12, fontWeight: 700 }}>Medium · B-14</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", padding: "12px 14px" }}>
              <span style={{ fontSize: 12, color: M_GRAY600 }}>Expires</span>
              <span style={{ fontSize: 12, fontWeight: 700 }}>27 May 2026</span>
            </div>
          </div>

          <div style={{ marginTop: 18, display: "flex", gap: 10, padding: 12, background: "#DDEDE6", borderRadius: 6 }}>
            <MIcon name="leaf" size={16} stroke={1.6} color="#006443" />
            <div style={{ fontSize: 12, color: "#0c4a32" }}><strong>GoGreen Plus</strong> · 1.4 kg CO₂e reduced.</div>
          </div>
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { MParcelsScreen, MDetailScreen, MScheduleScreen, MLockerScreen });

/* ──────────────────────────────────────────
   App — design canvas with 4 phone artboards
   ────────────────────────────────────────── */
function MobileKitApp() {
  return (
    <DesignCanvas style={{ background: "#1a1a1a" }}>
      <DCSection id="mobile" title="DHL App" subtitle="Recipient & sender — four canonical screens">
        <DCArtboard id="parcels"   label="01 · Parcels"          width={420} height={900}>
          <IOSDevice width={402} height={874} title="Parcels"><MParcelsScreen /></IOSDevice>
        </DCArtboard>
        <DCArtboard id="detail"    label="02 · Parcel detail"    width={420} height={900}>
          <IOSDevice width={402} height={874} title="Parcel"><MDetailScreen /></IOSDevice>
        </DCArtboard>
        <DCArtboard id="schedule"  label="03 · Schedule delivery" width={420} height={900}>
          <IOSDevice width={402} height={874} title="Schedule"><MScheduleScreen /></IOSDevice>
        </DCArtboard>
        <DCArtboard id="locker"    label="04 · Locker pickup"    width={420} height={900}>
          <IOSDevice width={402} height={874} title="Locker"><MLockerScreen /></IOSDevice>
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

Object.assign(window, { MobileKitApp });
