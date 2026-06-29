// DHL Express Tracking — page views
const { useState } = React;

/* ──────────────────────────────────────────
   HomePage — hero + service cards + secondary band
   ────────────────────────────────────────── */
function HomePage({ onTrack, openQuoteModal, openLocationModal }) {
  const [trackVal, setTrackVal] = useState("1234 5678 9012");
  return (
    <>
      <HeroTrack trackVal={trackVal} setTrackVal={setTrackVal} onTrack={onTrack} />

      {/* Service cards */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "72px 24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 28 }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--fg-muted)" }}>What we ship</div>
            <h2 style={{ fontSize: 36, fontWeight: 700, lineHeight: 1.1, margin: "8px 0 0" }}>Pick the service that fits.</h2>
          </div>
          <Button variant="link" iconRight="arrow-right">All services</Button>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16 }}>
          <ServiceCard icon="zap" eyebrow="Time definite" title="Express Worldwide" body="Door-to-door international shipping, by end of next business day." />
          <ServiceCard icon="package" eyebrow="Up to 70 kg" title="Parcel Domestic" body="Standard ground service across Germany. Track every step." />
          <ServiceCard variant="yellow" icon="globe" eyebrow="220+ countries" title="Global Forwarding" body="Air, ocean, and rail freight for time- and cost-critical lanes." />
          <ServiceCard variant="dark" icon="leaf" eyebrow="GoGreen Plus" title="Carbon-Reduced" body="Use sustainable aviation fuel and reduce your shipment's footprint." />
        </div>
      </section>

      {/* Split — image + copy */}
      <section style={{ background: "var(--dhl-gray-100)" }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", padding: "0 24px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 0, alignItems: "stretch", minHeight: 420 }}>
            <div style={{ background: `url('../../../pptx/assets/photography/photo_07.jpeg') center/cover no-repeat`, minHeight: 360 }} />
            <div style={{ background: "#fff", padding: "56px 48px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase", color: "var(--fg-muted)" }}>Send a parcel</div>
              <h2 style={{ fontSize: 42, fontWeight: 700, lineHeight: 1.05, margin: "10px 0 14px", maxWidth: 460 }}>
                A label in 90 seconds.
              </h2>
              <p style={{ fontSize: 16, lineHeight: 1.5, color: "var(--fg-muted)", margin: "0 0 24px", maxWidth: 460 }}>
                Enter weight and destination, pick a service, pay, print. Or drop your parcel off at any of 20,000+ Service Points.
              </p>
              <div style={{ display: "flex", gap: 12 }}>
                <Button variant="primary" size="lg" onClick={openQuoteModal}>Get a Quote</Button>
                <Button variant="ghost" size="lg" icon="map-pin" onClick={openLocationModal}>Find a Location</Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Reassurance row */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "72px 24px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 36 }}>
          {[
            { i: "shield-check", n: "98.4%", l: "on-time delivery, Q1 2026" },
            { i: "globe", n: "220+", l: "countries served" },
            { i: "truck", n: "1.7B", l: "parcels shipped yearly" },
            { i: "leaf", n: "GoGreen", l: "carbon-reduced lanes available" }
          ].map((m, i) => (
            <div key={i} style={{ borderLeft: "3px solid var(--dhl-red)", paddingLeft: 18 }}>
              <Icon name={m.i} size={22} stroke={1.5} style={{ color: "var(--dhl-red)" }} />
              <div style={{ fontFamily: "var(--font-display)", fontWeight: 900, fontSize: 44, lineHeight: 1, marginTop: 10 }}>{m.n}</div>
              <div style={{ fontSize: 13, color: "var(--fg-muted)", marginTop: 4 }}>{m.l}</div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}

/* ──────────────────────────────────────────
   TrackResultPage — summary + timeline + actions
   ────────────────────────────────────────── */
const SHIPMENT = {
  tn: "1234 5678 9012",
  status: "out",
  service: "Express Worldwide",
  weight: "2.4 kg",
  pieces: 1,
  from: { city: "Leipzig", country: "Germany" },
  to:   { city: "Lyon",    country: "France" },
  eta:  "Today, by 18:00",
  steps: [
    { label: "Picked up",        when: "Mon 14:02" },
    { label: "In transit",       when: "Tue 06:30" },
    { label: "Customs cleared",  when: "Wed 09:18" },
    { label: "Out for delivery", when: "Today 09:42" },
    { label: "Delivered",        when: "By 18:00" }
  ],
  currentIdx: 3,
  events: [
    { dt: "Today · 09:42",   loc: "Lyon, France",        code: "OFD",  body: "Out for delivery with courier 7184." , current: true },
    { dt: "Today · 06:55",   loc: "Lyon, France",        code: "AR",   body: "Arrived at local delivery facility." },
    { dt: "Wed · 23:14",     loc: "Lyon Saint-Exupéry",  code: "DP",   body: "Departed regional hub on flight DH7212." },
    { dt: "Wed · 09:18",     loc: "Lyon Saint-Exupéry",  code: "CC",   body: "Customs status updated — cleared for import." },
    { dt: "Tue · 22:30",     loc: "Leipzig, Germany",    code: "DP",   body: "Departed Leipzig EU Hub on flight DH0001." },
    { dt: "Tue · 06:30",     loc: "Leipzig, Germany",    code: "AR",   body: "Arrived at Leipzig EU Hub for sortation." },
    { dt: "Mon · 14:02",     loc: "Leipzig, Germany",    code: "PU",   body: "Shipment picked up by courier." }
  ]
};

function TrackResultPage({ onOpenDetail, onTrack }) {
  const [trackVal, setTrackVal] = useState(SHIPMENT.tn);
  const s = SHIPMENT;
  return (
    <>
      {/* Compact yellow band with input */}
      <section style={{ background: "var(--dhl-yellow)", padding: "32px 24px" }}>
        <div style={{ maxWidth: 1280, margin: "0 auto" }}>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(0,0,0,.55)", marginBottom: 10 }}>Tracking</div>
          <TrackingInput value={trackVal} onChange={setTrackVal} onSubmit={onTrack} />
        </div>
      </section>

      {/* Summary card */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "32px 24px 0" }}>
        <div style={{ background: "#fff", border: "1px solid var(--dhl-gray-200)", padding: 36 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 24, flexWrap: "wrap" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
                <ServiceLabel variant="black">{s.service}</ServiceLabel>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 13, color: "var(--fg-muted)" }}>{s.tn}</span>
              </div>
              <h1 style={{ fontFamily: "var(--font-display)", fontWeight: 900, fontSize: 56, lineHeight: 1, margin: "8px 0 4px", color: "#000" }}>
                Out for delivery.
              </h1>
              <p style={{ fontSize: 16, color: "var(--fg-muted)", margin: 0 }}>Expected <strong style={{ color: "#000" }}>{s.eta}</strong>.</p>
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <Button variant="primary" icon="bell">Notify me</Button>
              <Button variant="ghost" icon="share-2">Share</Button>
              <Button variant="ghost" icon="printer">Print</Button>
            </div>
          </div>

          <div style={{ height: 1, background: "var(--dhl-gray-150)", margin: "28px 0" }} />

          <Timeline steps={s.steps} currentIdx={s.currentIdx} />

          <div style={{ height: 1, background: "var(--dhl-gray-150)", margin: "28px 0" }} />

          <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr", gap: 24, alignItems: "center" }}>
            <AddressPair from={s.from} to={s.to} />
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--fg-muted)" }}>Weight</div>
              <div style={{ fontSize: 18, fontWeight: 700, marginTop: 4 }}>{s.weight}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--fg-muted)" }}>Pieces</div>
              <div style={{ fontSize: 18, fontWeight: 700, marginTop: 4 }}>{s.pieces}</div>
            </div>
            <div>
              <Button variant="link" iconRight="arrow-right" onClick={onOpenDetail}>Full event history</Button>
            </div>
          </div>
        </div>
      </section>

      {/* GoGreen note */}
      <section style={{ maxWidth: 1280, margin: "0 auto", padding: "32px 24px" }}>
        <div style={{ display: "flex", gap: 24, alignItems: "center", padding: "20px 28px", background: "#DDEDE6", borderLeft: "4px solid var(--dhl-green)" }}>
          <Icon name="leaf" size={28} stroke={1.5} style={{ color: "var(--dhl-green)" }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: "var(--dhl-green)" }}>This shipment uses GoGreen Plus</div>
            <div style={{ fontSize: 12, color: "#0c4a32", marginTop: 2 }}>1.4 kg CO₂e reduced through Sustainable Aviation Fuel.</div>
          </div>
          <Button variant="link" iconRight="arrow-right" style={{ color: "var(--dhl-green)" }}>About GoGreen</Button>
        </div>
      </section>
    </>
  );
}

/* ──────────────────────────────────────────
   DetailPage — full event history
   ────────────────────────────────────────── */
function DetailPage({ onBack }) {
  const s = SHIPMENT;
  return (
    <section style={{ maxWidth: 1280, margin: "0 auto", padding: "32px 24px" }}>
      <Button variant="link" icon="arrow-left" onClick={onBack}>Back to summary</Button>

      <div style={{ background: "#fff", border: "1px solid var(--dhl-gray-200)", padding: 36, marginTop: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
          <div>
            <ServiceLabel variant="black">{s.service}</ServiceLabel>
            <h1 style={{ fontFamily: "var(--font-sans)", fontWeight: 700, fontSize: 28, lineHeight: 1.1, margin: "10px 0 4px" }}>Event history</h1>
            <div style={{ fontSize: 13, color: "var(--fg-muted)", fontFamily: "var(--font-mono)" }}>{s.tn}</div>
          </div>
          <StatusChip status={s.status} />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "150px 1fr 1fr 80px", gap: 24, padding: "10px 0", borderBottom: "1px solid var(--dhl-gray-300)", fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--fg-muted)" }}>
          <span>Date / Time</span><span>Event</span><span>Location</span><span style={{ textAlign: "right" }}>Code</span>
        </div>
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {s.events.map((e, i) => (
            <EventRow key={i} datetime={e.dt} location={e.loc} code={e.code} body={e.body} current={e.current} />
          ))}
        </ul>
      </div>
    </section>
  );
}

/* ──────────────────────────────────────────
   App shell — routing between views + modals
   ────────────────────────────────────────── */
function App() {
  const [view, setView] = useState("home");      // home | track | detail
  const [quoteOpen, setQuoteOpen] = useState(false);
  const [locOpen, setLocOpen] = useState(false);

  const handleNav = (id) => {
    if (id === "home") setView("home");
    if (id === "track") setView("track");
    if (id === "ship") setQuoteOpen(true);
    if (id === "locate") setLocOpen(true);
  };
  const handleTrack = (val) => { setView("track"); };

  return (
    <div style={{ background: "#fff", minHeight: "100vh" }}>
      <Header onNav={handleNav} current={view === "home" ? "home" : view === "detail" ? "track" : view} />
      {view === "home"   && <HomePage onTrack={handleTrack} openQuoteModal={() => setQuoteOpen(true)} openLocationModal={() => setLocOpen(true)} />}
      {view === "track"  && <TrackResultPage onOpenDetail={() => setView("detail")} onTrack={handleTrack} />}
      {view === "detail" && <DetailPage onBack={() => setView("track")} />}
      <Footer />

      <Modal open={quoteOpen} onClose={() => setQuoteOpen(false)} title="Get a Quote" width={580}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <Field label="From (postal code)"><Input defaultValue="04103" /></Field>
          <Field label="To (postal code)"><Input defaultValue="69002" /></Field>
          <Field label="Country of origin"><Select defaultValue="DE" options={[{value:"DE",label:"Germany"},{value:"FR",label:"France"},{value:"US",label:"United States"}]} /></Field>
          <Field label="Destination country"><Select defaultValue="FR" options={[{value:"DE",label:"Germany"},{value:"FR",label:"France"},{value:"US",label:"United States"}]} /></Field>
          <Field label="Weight (kg)"><Input type="number" defaultValue="2.4" /></Field>
          <Field label="Service"><Select options={["Express 9:00","Express 12:00","Express Worldwide","Economy Select"]} /></Field>
        </div>
        <div style={{ borderTop: "1px solid var(--dhl-gray-150)", marginTop: 24, paddingTop: 18, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--fg-muted)" }}>Estimated</div>
            <div style={{ fontFamily: "var(--font-display)", fontWeight: 900, fontSize: 32, lineHeight: 1, marginTop: 4 }}>€24.50 <span style={{ fontSize: 14, fontWeight: 400, color: "var(--fg-muted)" }}>EUR</span></div>
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <Button variant="ghost" onClick={() => setQuoteOpen(false)}>Cancel</Button>
            <Button variant="primary" iconRight="arrow-right">Continue</Button>
          </div>
        </div>
      </Modal>

      <Modal open={locOpen} onClose={() => setLocOpen(false)} title="Find a Location" width={520}>
        <Field label="Search city, postal code, or address"><Input defaultValue="Lyon, France" /></Field>
        <div style={{ marginTop: 18 }}>
          <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--fg-muted)", marginBottom: 10 }}>Nearby</div>
          <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 0 }}>
            {[
              { name: "DHL ServicePoint Lyon Bellecour", addr: "12 rue de la République, 69002 Lyon", dist: "0.4 km", type: "ServicePoint" },
              { name: "DHL Parcel Locker Part-Dieu",     addr: "Gare Part-Dieu, 69003 Lyon",          dist: "1.8 km", type: "Locker" },
              { name: "DHL Express Service Centre",     addr: "8 quai Perrache, 69002 Lyon",         dist: "2.6 km", type: "Express" }
            ].map((l, i) => (
              <li key={i} style={{ display: "grid", gridTemplateColumns: "1fr 80px", gap: 12, padding: "14px 0", borderBottom: "1px solid var(--dhl-gray-150)" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                    <ServiceLabel variant={l.type === "Express" ? "red" : "ghost"}>{l.type}</ServiceLabel>
                    <span style={{ fontSize: 14, fontWeight: 700 }}>{l.name}</span>
                  </div>
                  <div style={{ fontSize: 12, color: "var(--fg-muted)" }}>{l.addr}</div>
                </div>
                <div style={{ textAlign: "right", fontSize: 13, color: "var(--fg-muted)", alignSelf: "center" }}>{l.dist}</div>
              </li>
            ))}
          </ul>
        </div>
      </Modal>
    </div>
  );
}

Object.assign(window, { HomePage, TrackResultPage, DetailPage, App });
