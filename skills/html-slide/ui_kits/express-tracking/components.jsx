// DHL Express Tracking — shared components
// All components exported to `window` at the bottom for cross-file use.

const { useState, useEffect, useRef } = React;

/* ─────────────────────────────────────────────
   Icon — small Lucide wrapper
   ───────────────────────────────────────────── */
function Icon({ name, size = 20, color = "currentColor", stroke = 1.5, ...rest }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current && window.lucide) {
      ref.current.innerHTML = "";
      const el = document.createElement("i");
      el.setAttribute("data-lucide", name);
      el.style.width = size + "px";
      el.style.height = size + "px";
      el.style.color = color;
      el.style.strokeWidth = stroke;
      ref.current.appendChild(el);
      window.lucide.createIcons({ attrs: { width: size, height: size, "stroke-width": stroke } });
    }
  }, [name, size, color, stroke]);
  return <span ref={ref} style={{ display: "inline-flex", lineHeight: 0, ...rest.style }} {...rest} />;
}

/* ─────────────────────────────────────────────
   Button
   ───────────────────────────────────────────── */
function Button({ variant = "primary", size = "md", icon, iconRight, children, onClick, disabled, type = "button", style }) {
  const base = {
    fontFamily: "var(--font-sans)",
    fontWeight: 700,
    border: 0,
    cursor: disabled ? "not-allowed" : "pointer",
    borderRadius: 4,
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    letterSpacing: ".01em",
    transition: "background 160ms var(--ease-standard), color 160ms var(--ease-standard)",
    opacity: disabled ? 0.4 : 1,
    whiteSpace: "nowrap"
  };
  const sizes = {
    sm: { padding: "7px 12px", fontSize: 12 },
    md: { padding: "11px 18px", fontSize: 14 },
    lg: { padding: "14px 24px", fontSize: 15 }
  };
  const variants = {
    primary: { background: "var(--dhl-red)", color: "#fff" },
    primaryHover: { background: "#BD0510" },
    secondary: { background: "#000", color: "#fff" },
    ghost: { background: "transparent", color: "#000", border: "1.5px solid #000" },
    link: { background: "transparent", color: "var(--dhl-red)", textDecoration: "underline", textUnderlineOffset: 2, padding: "8px 4px" }
  };
  const [hover, setHover] = useState(false);
  const v = variants[variant] || variants.primary;
  const vh = hover && variant === "primary" ? variants.primaryHover : (hover && variant === "secondary" ? { background: "#222" } : (hover && variant === "ghost" ? { background: "rgba(0,0,0,.06)" } : null));
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{ ...base, ...sizes[size], ...v, ...vh, ...(variant === "link" ? { padding: "8px 4px" } : {}), ...style }}
    >
      {icon && <Icon name={icon} size={size === "sm" ? 14 : 16} stroke={1.75} />}
      <span>{children}</span>
      {iconRight && <Icon name={iconRight} size={size === "sm" ? 14 : 16} stroke={1.75} />}
    </button>
  );
}

/* ─────────────────────────────────────────────
   Field / Select / Input
   ───────────────────────────────────────────── */
function Field({ label, hint, error, children }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      {label && <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".02em" }}>{label}</span>}
      {children}
      {(hint || error) && (
        <span style={{ fontSize: 11, color: error ? "var(--dhl-red)" : "var(--fg-muted)" }}>{error || hint}</span>
      )}
    </label>
  );
}
function inputStyle(error) {
  return {
    font: "400 14px var(--font-sans)",
    padding: "10px 12px",
    border: `1px solid ${error ? "var(--dhl-red)" : "var(--dhl-gray-300)"}`,
    borderRadius: 4,
    background: "#fff",
    color: "#000",
    outline: "none"
  };
}
function Input({ error, ...rest }) { return <input style={inputStyle(error)} {...rest} />; }
function Select({ error, options = [], ...rest }) {
  return <select style={inputStyle(error)} {...rest}>{options.map(o => <option key={o.value || o} value={o.value || o}>{o.label || o}</option>)}</select>;
}

/* ─────────────────────────────────────────────
   StatusChip
   ───────────────────────────────────────────── */
const STATUS = {
  delivered:  { bg: "#DDEDE6", fg: "#006443", label: "Delivered" },
  out:        { bg: "#FFCC00", fg: "#000",    label: "Out for Delivery" },
  transit:    { bg: "#F2F2F2", fg: "#333",    label: "In Transit" },
  pickup:     { bg: "#FBE0E2", fg: "#A30410", label: "Awaiting Pickup" },
  exception:  { bg: "#FBE0E2", fg: "#A30410", label: "Exception" },
  scheduled:  { bg: "#F2F2F2", fg: "#666",    label: "Scheduled" }
};
function StatusChip({ status = "transit", label }) {
  const s = STATUS[status] || STATUS.transit;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      padding: "5px 12px", borderRadius: 999,
      font: "700 11px/1 var(--font-sans)",
      letterSpacing: ".06em", textTransform: "uppercase",
      background: s.bg, color: s.fg
    }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: s.fg }} />
      {label || s.label}
    </span>
  );
}

/* ─────────────────────────────────────────────
   ServiceLabel — small black/red square label
   ───────────────────────────────────────────── */
function ServiceLabel({ children, variant = "black" }) {
  const v = variant === "red"
    ? { background: "var(--dhl-red)", color: "#fff" }
    : variant === "ghost"
      ? { background: "transparent", color: "#000", border: "1.5px solid #000" }
      : { background: "#000", color: "#fff" };
  return (
    <span style={{
      display: "inline-block",
      padding: "3px 8px",
      font: "700 10px/1.4 var(--font-sans)",
      letterSpacing: ".06em",
      textTransform: "uppercase",
      borderRadius: 2,
      ...v
    }}>{children}</span>
  );
}

/* ─────────────────────────────────────────────
   Header
   ───────────────────────────────────────────── */
function Header({ onNav, current = "track" }) {
  const items = [
    { id: "ship",    label: "Ship" },
    { id: "track",   label: "Track" },
    { id: "locate",  label: "Find a Location" },
    { id: "business",label: "For Business" },
    { id: "help",    label: "Help" }
  ];
  return (
    <header style={{
      background: "#fff",
      borderBottom: "1px solid var(--dhl-gray-200)",
      position: "sticky", top: 0, zIndex: 50
    }}>
      <div style={{ background: "#000", color: "#fff", fontSize: 11, letterSpacing: ".04em" }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", padding: "6px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>DHL Group · <span style={{ opacity: .65 }}>Express · eCommerce · Global Forwarding · Supply Chain</span></span>
          <span style={{ display: "inline-flex", gap: 18, alignItems: "center", opacity: .85 }}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}><Icon name="globe" size={12} stroke={1.75} /> Germany · EN</span>
            <span>Customer Portal</span>
          </span>
        </div>
      </div>
      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "14px 24px", display: "flex", alignItems: "center", gap: 32 }}>
        <a onClick={() => onNav?.("home")} style={{ cursor: "pointer", display: "flex", alignItems: "center" }}>
          <img src="../../../pptx/assets/logos/DHL_Logo_rgb.svg" alt="DHL" style={{ height: 28 }} />
        </a>
        <nav style={{ display: "flex", gap: 24, marginLeft: 12 }}>
          {items.map(it => (
            <a key={it.id} onClick={() => onNav?.(it.id)} style={{
              fontSize: 14, fontWeight: 700,
              padding: "6px 0",
              borderBottom: current === it.id ? "3px solid var(--dhl-red)" : "3px solid transparent",
              color: "#000", cursor: "pointer", textDecoration: "none"
            }}>{it.label}</a>
          ))}
        </nav>
        <div style={{ marginLeft: "auto", display: "flex", gap: 14, alignItems: "center" }}>
          <Icon name="search" size={20} stroke={1.5} style={{ cursor: "pointer" }} />
          <Button variant="ghost" size="sm" icon="user">Sign in</Button>
        </div>
      </div>
    </header>
  );
}

/* ─────────────────────────────────────────────
   Footer
   ───────────────────────────────────────────── */
function Footer() {
  return (
    <footer style={{ background: "#000", color: "#fff", marginTop: 80 }}>
      <div style={{ background: "var(--dhl-yellow)", padding: "48px 24px" }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 24, color: "#000" }}>
          <div style={{ fontFamily: "var(--font-display)", fontWeight: 900, fontSize: 40, lineHeight: 1, maxWidth: 700 }}>
            Excellence.<br/>Simply delivered.
          </div>
          <div style={{ display: "flex", gap: 12 }}>
            <Button variant="secondary" size="lg" icon="package">Send a Shipment</Button>
            <Button variant="ghost" size="lg" icon="map-pin">Find a Location</Button>
          </div>
        </div>
      </div>
      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "48px 24px", display: "grid", gridTemplateColumns: "1.5fr 1fr 1fr 1fr 1fr", gap: 36 }}>
        <div>
          <img src="../../../pptx/assets/logos/DHL_Logo_white_rgb.svg" alt="DHL" style={{ height: 28, filter: "brightness(0) invert(1)" }} />
          <p style={{ fontSize: 12, lineHeight: 1.5, opacity: .7, marginTop: 18 }}>
            DHL is the global market leader of the international express and logistics industry.
          </p>
        </div>
        <FooterCol title="Ship" items={["Send a Shipment","Get a Quote","Surcharges","Customs"]} />
        <FooterCol title="Track" items={["Track Shipment","Track by Reference","Proof of Delivery","Tracking API"]} />
        <FooterCol title="Manage" items={["My DHL+","Address Book","Billing","Settings"]} />
        <FooterCol title="About" items={["DHL Group","Sustainability","Careers","Press"]} />
      </div>
      <div style={{ borderTop: "1px solid rgba(255,255,255,.12)", padding: "20px 24px" }}>
        <div style={{ maxWidth: 1280, margin: "0 auto", display: "flex", justifyContent: "space-between", fontSize: 11, color: "rgba(255,255,255,.55)" }}>
          <span>© 2026 Deutsche Post AG · All rights reserved</span>
          <span>Imprint · Terms · Privacy · Cookie Settings</span>
        </div>
      </div>
    </footer>
  );
}
function FooterCol({ title, items }) {
  return (
    <div>
      <h4 style={{ fontSize: 13, fontWeight: 700, marginBottom: 14, color: "#fff" }}>{title}</h4>
      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 8 }}>
        {items.map(i => <li key={i}><a style={{ color: "rgba(255,255,255,.7)", fontSize: 13, textDecoration: "none", cursor: "pointer" }}>{i}</a></li>)}
      </ul>
    </div>
  );
}

/* ─────────────────────────────────────────────
   TrackingInput — used in hero + result bar
   ───────────────────────────────────────────── */
function TrackingInput({ value, onChange, onSubmit, dark }) {
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit?.(value); }}
      style={{
        display: "flex", gap: 0,
        background: "#fff",
        border: dark ? "1px solid transparent" : "2px solid #000",
        borderRadius: 4, overflow: "hidden",
        maxWidth: 640, width: "100%"
      }}>
      <Icon name="package" size={22} stroke={1.5} style={{ alignSelf: "center", marginLeft: 14, color: "#000" }} />
      <input
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder="Tracking number, e.g. 1234 5678 9012"
        style={{ flex: 1, border: 0, outline: 0, font: "400 16px var(--font-sans)", padding: "16px 14px", background: "transparent", letterSpacing: ".02em" }}
      />
      <button type="submit" style={{ border: 0, background: "var(--dhl-red)", color: "#fff", padding: "0 28px", font: "700 14px var(--font-sans)", cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}>
        Track <Icon name="arrow-right" size={16} stroke={2} />
      </button>
    </form>
  );
}

/* ─────────────────────────────────────────────
   HeroTrack — yellow hero with tracking input
   ───────────────────────────────────────────── */
function HeroTrack({ trackVal, setTrackVal, onTrack }) {
  return (
    <section style={{ background: "var(--dhl-yellow)", position: "relative", overflow: "hidden" }}>
      {/* Chevron in corner */}
      <svg style={{ position: "absolute", right: -60, top: "50%", transform: "translateY(-50%)", height: 480, opacity: .9 }} viewBox="0 0 240 480">
        <g fill="#D40511">
          <path d="M0 60 L 80 0 L 130 0 L 50 60 L 130 120 L 80 120 Z" opacity=".35" transform="translate(0 130)"/>
          <path d="M60 60 L 140 0 L 190 0 L 110 60 L 190 120 L 140 120 Z" opacity=".7" transform="translate(0 130)"/>
          <path d="M120 60 L 200 0 L 250 0 L 170 60 L 250 120 L 200 120 Z" transform="translate(0 130)"/>
        </g>
      </svg>

      <div style={{ maxWidth: 1280, margin: "0 auto", padding: "88px 24px 80px", position: "relative", zIndex: 1 }}>
        <div style={{ fontSize: 13, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(0,0,0,.55)" }}>Track a shipment</div>
        <h1 style={{
          fontFamily: "var(--font-display)", fontWeight: 900,
          fontSize: 72, lineHeight: .98, letterSpacing: "-.01em",
          margin: "14px 0 18px", maxWidth: 820
        }}>
          Find your<br/>parcel in seconds.
        </h1>
        <p style={{ fontSize: 18, lineHeight: 1.4, maxWidth: 560, color: "rgba(0,0,0,.78)", margin: "0 0 36px" }}>
          Drop in a tracking number — we'll show every stop from pickup to your door.
        </p>
        <TrackingInput value={trackVal} onChange={setTrackVal} onSubmit={onTrack} />
        <div style={{ marginTop: 16, display: "flex", gap: 22, fontSize: 13, fontWeight: 700, alignItems: "center" }}>
          <a style={{ color: "#000", textDecoration: "underline", cursor: "pointer" }}>Track by reference</a>
          <span style={{ opacity: .35 }}>·</span>
          <a style={{ color: "#000", textDecoration: "underline", cursor: "pointer" }}>Multiple shipments</a>
        </div>
      </div>
    </section>
  );
}

/* ─────────────────────────────────────────────
   ServiceCard
   ───────────────────────────────────────────── */
function ServiceCard({ icon, eyebrow, title, body, cta = "Learn more", variant = "white" }) {
  const isYellow = variant === "yellow";
  const isDark = variant === "dark";
  const bg = isYellow ? "var(--dhl-yellow)" : isDark ? "#000" : "#fff";
  const fg = isDark ? "#fff" : "#000";
  const acc = isDark ? "var(--dhl-yellow)" : "var(--dhl-red)";
  return (
    <div style={{
      background: bg, color: fg,
      padding: 28,
      border: isYellow || isDark ? "1px solid transparent" : "1px solid var(--dhl-gray-200)",
      display: "flex", flexDirection: "column", gap: 12, minHeight: 240
    }}>
      <Icon name={icon} size={36} stroke={1.4} color={acc} />
      <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase", color: isDark ? "rgba(255,255,255,.6)" : "var(--fg-muted)" }}>{eyebrow}</div>
      <h3 style={{ fontSize: 22, fontWeight: 700, lineHeight: 1.15, margin: 0 }}>{title}</h3>
      <p style={{ fontSize: 14, lineHeight: 1.45, color: isDark ? "rgba(255,255,255,.75)" : "var(--fg-muted)", margin: 0 }}>{body}</p>
      <a style={{ marginTop: "auto", color: acc, fontWeight: 700, fontSize: 13, textDecoration: "none", display: "inline-flex", alignItems: "center", gap: 6, cursor: "pointer" }}>
        {cta} <Icon name="arrow-right" size={14} stroke={2} />
      </a>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Timeline — horizontal stepper
   ───────────────────────────────────────────── */
function Timeline({ steps, currentIdx = 0 }) {
  return (
    <div style={{ width: "100%" }}>
      <div style={{ position: "relative", display: "flex", justifyContent: "space-between", alignItems: "center", padding: "20px 0" }}>
        {/* full line */}
        <div style={{ position: "absolute", left: 12, right: 12, top: "50%", height: 2, background: "var(--dhl-gray-200)" }} />
        {/* progress */}
        <div style={{ position: "absolute", left: 12, top: "50%", height: 2, background: "var(--dhl-red)",
          width: `calc(${(currentIdx / (steps.length - 1)) * 100}% - 12px)`, transition: "width 240ms var(--ease-standard)" }} />
        {steps.map((s, i) => {
          const done = i < currentIdx;
          const active = i === currentIdx;
          return (
            <div key={i} style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
              <span style={{
                width: 14, height: 14, borderRadius: "50%",
                background: active ? "#fff" : (done ? "var(--dhl-red)" : "var(--dhl-gray-300)"),
                boxShadow: active ? "0 0 0 4px var(--dhl-red)" : `0 0 0 1px ${done ? "var(--dhl-red)" : "var(--dhl-gray-300)"}`,
                border: "2px solid #fff",
                transform: active ? "scale(1.05)" : "none"
              }} />
            </div>
          );
        })}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        {steps.map((s, i) => (
          <div key={i} style={{ flex: 1, textAlign: "center", padding: "0 4px" }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: i === currentIdx ? "#000" : "var(--fg-muted)" }}>{s.label}</div>
            <div style={{ fontSize: 10, fontFamily: "var(--font-mono)", color: "var(--fg-subtle)", marginTop: 2 }}>{s.when}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   EventRow — event history list
   ───────────────────────────────────────────── */
function EventRow({ datetime, location, code, body, current }) {
  return (
    <li style={{ display: "grid", gridTemplateColumns: "150px 1fr 1fr 80px", gap: 24, padding: "16px 0", borderBottom: "1px solid var(--dhl-gray-150)", alignItems: "baseline" }}>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: current ? "var(--dhl-red)" : "var(--fg-muted)", fontWeight: current ? 700 : 400 }}>{datetime}</span>
      <span style={{ fontSize: 14, fontWeight: current ? 700 : 400 }}>{body}</span>
      <span style={{ fontSize: 13, color: "var(--fg-muted)" }}>{location}</span>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--fg-subtle)", textAlign: "right" }}>{code}</span>
    </li>
  );
}

/* ─────────────────────────────────────────────
   Modal
   ───────────────────────────────────────────── */
function Modal({ open, onClose, title, children, width = 520 }) {
  if (!open) return null;
  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,.55)",
      display: "flex", alignItems: "center", justifyContent: "center",
      zIndex: 100, padding: 20
    }}>
      <div onClick={(e) => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 6, width, maxWidth: "100%",
        boxShadow: "0 24px 60px rgba(0,0,0,.25)",
        overflow: "hidden"
      }}>
        <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--dhl-gray-150)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>{title}</h3>
          <button onClick={onClose} style={{ border: 0, background: "transparent", cursor: "pointer", padding: 4, display: "flex" }}><Icon name="x" size={20} /></button>
        </div>
        <div style={{ padding: 24 }}>{children}</div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Address pair — From / To
   ───────────────────────────────────────────── */
function AddressPair({ from, to }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 60px 1fr", alignItems: "center", gap: 8 }}>
      <div>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--fg-muted)" }}>From</div>
        <div style={{ fontSize: 18, fontWeight: 700, marginTop: 4 }}>{from.city}</div>
        <div style={{ fontSize: 12, color: "var(--fg-muted)", marginTop: 2 }}>{from.country}</div>
      </div>
      <div style={{ display: "flex", justifyContent: "center", color: "var(--dhl-red)" }}>
        <Icon name="arrow-right" size={28} stroke={2} />
      </div>
      <div>
        <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".06em", textTransform: "uppercase", color: "var(--fg-muted)" }}>To</div>
        <div style={{ fontSize: 18, fontWeight: 700, marginTop: 4 }}>{to.city}</div>
        <div style={{ fontSize: 12, color: "var(--fg-muted)", marginTop: 2 }}>{to.country}</div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Export to window
   ───────────────────────────────────────────── */
Object.assign(window, {
  Icon, Button, Field, Input, Select,
  StatusChip, ServiceLabel,
  Header, Footer, FooterCol,
  TrackingInput, HeroTrack, ServiceCard,
  Timeline, EventRow, Modal, AddressPair
});
