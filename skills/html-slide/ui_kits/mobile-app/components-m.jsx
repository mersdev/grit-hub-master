// DHL Mobile UI Kit — components
const { useState } = React;

const M_RED    = "#D40511";
const M_YELLOW = "#FFCC00";
const M_GRAY100 = "#F2F2F2";
const M_GRAY150 = "#EBEBEB";
const M_GRAY200 = "#E5E5E5";
const M_GRAY300 = "#CCCCCC";
const M_GRAY500 = "#8C8C8C";
const M_GRAY600 = "#666666";
const M_GRAY800 = "#333333";

const M_FONT = "'Delivery', -apple-system, sans-serif";

/* MIcon — Lucide */
function MIcon({ name, size = 20, color = "currentColor", stroke = 1.6, style }) {
  const ref = React.useRef(null);
  React.useEffect(() => {
    if (ref.current && window.lucide) {
      ref.current.innerHTML = "";
      const i = document.createElement("i");
      i.setAttribute("data-lucide", name);
      ref.current.appendChild(i);
      window.lucide.createIcons({ attrs: { width: size, height: size, "stroke-width": stroke, stroke: color } });
    }
  }, [name, size, color, stroke]);
  return <span ref={ref} style={{ display: "inline-flex", lineHeight: 0, color, ...style }} />;
}

/* MobileHeader — yellow brand bar */
function MobileHeader({ title, leading, trailing, subtitle }) {
  return (
    <div style={{ background: M_YELLOW, padding: "14px 18px 18px", color: "#000" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", height: 28 }}>
        <div style={{ width: 32, display: "flex", justifyContent: "flex-start", alignItems: "center" }}>
          {leading || <img src="../../../pptx/assets/logos/DHL_Logo_rgb.svg" alt="DHL" style={{ height: 14 }} />}
        </div>
        <div style={{ fontSize: 14, fontWeight: 700, letterSpacing: ".02em" }}>{title}</div>
        <div style={{ width: 32, display: "flex", justifyContent: "flex-end" }}>
          {trailing || <MIcon name="bell" size={20} color="#000" stroke={1.75} />}
        </div>
      </div>
      {subtitle && (
        <div style={{ fontSize: 24, fontWeight: 700, fontFamily: "var(--font-display)", lineHeight: 1.1, marginTop: 10, color: "#000" }}>
          {subtitle}
        </div>
      )}
    </div>
  );
}

/* MStatusChip — smaller for mobile */
function MStatusChip({ status = "transit" }) {
  const map = {
    out:       { bg: M_YELLOW,   fg: "#000",    label: "Out for delivery" },
    delivered: { bg: "#DDEDE6",  fg: "#006443", label: "Delivered" },
    transit:   { bg: M_GRAY100,  fg: "#333",    label: "In transit" },
    pickup:    { bg: "#FBE0E2",  fg: "#A30410", label: "Ready for pickup" },
    scheduled: { bg: M_GRAY100,  fg: "#666",    label: "Scheduled" },
    exception: { bg: "#FBE0E2",  fg: "#A30410", label: "Exception" }
  };
  const s = map[status] || map.transit;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      padding: "3px 9px", borderRadius: 999,
      font: `700 10px/1 ${M_FONT}`, letterSpacing: ".06em", textTransform: "uppercase",
      background: s.bg, color: s.fg
    }}>
      <span style={{ width: 5, height: 5, borderRadius: "50%", background: s.fg }} />
      {s.label}
    </span>
  );
}

/* MLabel — square inline tag */
function MLabel({ children, variant = "black" }) {
  const styles = variant === "red"
    ? { background: M_RED, color: "#fff" }
    : variant === "ghost"
      ? { background: "transparent", color: "#000", border: "1.25px solid #000" }
      : { background: "#000", color: "#fff" };
  return (
    <span style={{
      display: "inline-block",
      padding: "2px 7px",
      font: `700 9px/1.3 ${M_FONT}`,
      letterSpacing: ".06em", textTransform: "uppercase",
      borderRadius: 2, ...styles
    }}>{children}</span>
  );
}

/* MButton */
function MButton({ children, variant = "primary", icon, iconRight, onClick, fullWidth, size = "md" }) {
  const variants = {
    primary:   { background: M_RED, color: "#fff" },
    secondary: { background: "#000", color: "#fff" },
    ghost:     { background: "transparent", color: "#000", border: "1.5px solid #000" },
    yellow:    { background: M_YELLOW, color: "#000" }
  };
  const sizes = {
    sm: { padding: "8px 14px", fontSize: 13 },
    md: { padding: "12px 18px", fontSize: 14 },
    lg: { padding: "16px 22px", fontSize: 15 }
  };
  return (
    <button onClick={onClick} style={{
      ...variants[variant], ...sizes[size],
      border: variants[variant].border || "0",
      borderRadius: 6, fontFamily: M_FONT, fontWeight: 700,
      width: fullWidth ? "100%" : "auto",
      display: "inline-flex", alignItems: "center", justifyContent: "center", gap: 8,
      cursor: "pointer", letterSpacing: ".01em"
    }}>
      {icon && <MIcon name={icon} size={16} stroke={1.75} color="currentColor" />}
      {children}
      {iconRight && <MIcon name={iconRight} size={16} stroke={2} color="currentColor" />}
    </button>
  );
}

/* ParcelRow — list item */
function ParcelRow({ sender, tn, status, eta, service, onClick, accent }) {
  return (
    <div onClick={onClick} style={{
      display: "flex", gap: 14, padding: "16px 18px",
      borderBottom: `1px solid ${M_GRAY150}`, cursor: "pointer", background: "#fff",
      position: "relative"
    }}>
      {accent && <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 3, background: M_RED }} />}
      <div style={{
        width: 44, height: 44, background: M_YELLOW, borderRadius: 6,
        display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0
      }}>
        <MIcon name="package" size={22} color="#000" stroke={1.5} />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "baseline" }}>
          <div style={{ fontSize: 15, fontWeight: 700, color: "#000", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{sender}</div>
          <MIcon name="chevron-right" size={16} color={M_GRAY500} stroke={1.75} style={{ flexShrink: 0 }} />
        </div>
        <div style={{ fontSize: 11, color: M_GRAY600, fontFamily: "var(--font-mono)", letterSpacing: ".04em", marginTop: 2 }}>{tn}</div>
        <div style={{ display: "flex", gap: 8, marginTop: 8, alignItems: "center", flexWrap: "wrap" }}>
          <MStatusChip status={status} />
          <span style={{ fontSize: 11, color: M_GRAY600 }}>· {eta}</span>
        </div>
      </div>
    </div>
  );
}

/* VTimeline — vertical tracking stepper */
function VTimeline({ events }) {
  return (
    <ol style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {events.map((e, i) => {
        const isLast = i === events.length - 1;
        const isFirst = i === 0;
        const lineColor = e.done ? M_RED : M_GRAY300;
        return (
          <li key={i} style={{ display: "grid", gridTemplateColumns: "32px 1fr", gap: 0, position: "relative" }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
              <span style={{
                width: e.current ? 16 : 10,
                height: e.current ? 16 : 10,
                borderRadius: "50%",
                background: e.current ? "#fff" : (e.done ? M_RED : M_GRAY300),
                boxShadow: e.current ? `0 0 0 4px ${M_RED}` : "none",
                marginTop: isFirst ? 4 : 8
              }} />
              {!isLast && <span style={{ flex: 1, width: 2, background: lineColor, marginTop: 6 }} />}
            </div>
            <div style={{ padding: "0 0 22px 14px" }}>
              <div style={{ fontSize: 14, fontWeight: e.current ? 700 : 500, color: "#000" }}>{e.label}</div>
              <div style={{ fontSize: 12, color: M_GRAY600, marginTop: 2 }}>{e.location}</div>
              <div style={{ fontSize: 11, color: M_GRAY500, fontFamily: "var(--font-mono)", marginTop: 2 }}>{e.when}</div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

/* ScheduleOption — radio row */
function ScheduleOption({ icon, title, sub, value, selectedValue, onClick }) {
  const selected = value === selectedValue;
  return (
    <div onClick={() => onClick(value)} style={{
      display: "flex", gap: 12, padding: 14, alignItems: "center",
      background: selected ? "#FFF5CC" : "#fff",
      border: `1.5px solid ${selected ? M_RED : M_GRAY200}`,
      borderRadius: 6, cursor: "pointer", marginBottom: 8
    }}>
      <div style={{ width: 36, height: 36, background: selected ? M_YELLOW : M_GRAY100, borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <MIcon name={icon} size={18} stroke={1.6} color="#000" />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 14, fontWeight: 700 }}>{title}</div>
        <div style={{ fontSize: 12, color: M_GRAY600, marginTop: 1 }}>{sub}</div>
      </div>
      <span style={{
        width: 18, height: 18, borderRadius: "50%",
        border: `2px solid ${selected ? M_RED : M_GRAY300}`,
        background: selected ? M_RED : "transparent",
        boxShadow: selected ? "inset 0 0 0 3px #fff" : "none"
      }} />
    </div>
  );
}

/* BottomNav — 4 tabs */
function BottomNav({ current = "parcels" }) {
  const items = [
    { id: "parcels",  label: "Parcels",  icon: "package" },
    { id: "ship",     label: "Ship",     icon: "send" },
    { id: "locate",   label: "Locate",   icon: "map-pin" },
    { id: "account",  label: "Account",  icon: "user" }
  ];
  return (
    <div style={{
      position: "absolute", bottom: 0, left: 0, right: 0,
      background: "#fff", borderTop: `1px solid ${M_GRAY150}`,
      display: "flex", justifyContent: "space-around", paddingTop: 8, paddingBottom: 28
    }}>
      {items.map(it => {
        const active = it.id === current;
        return (
          <div key={it.id} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 3, cursor: "pointer" }}>
            <MIcon name={it.icon} size={22} stroke={active ? 2 : 1.5} color={active ? M_RED : M_GRAY600} />
            <span style={{ fontSize: 10, fontWeight: 700, color: active ? M_RED : M_GRAY600 }}>{it.label}</span>
          </div>
        );
      })}
    </div>
  );
}

/* QRPanel */
function QRPanel({ code, locker, addr }) {
  return (
    <div style={{ background: M_YELLOW, padding: 24, display: "flex", flexDirection: "column", alignItems: "center", gap: 14 }}>
      <div style={{ fontSize: 11, fontWeight: 700, letterSpacing: ".08em", textTransform: "uppercase", color: "rgba(0,0,0,.55)" }}>Show this at locker</div>
      <div style={{ background: "#fff", padding: 16, borderRadius: 6 }}>
        {/* QR placeholder */}
        <svg width="160" height="160" viewBox="0 0 32 32" shapeRendering="crispEdges">
          {(() => {
            // simple deterministic pattern
            const cells = [];
            for (let y = 0; y < 32; y++) {
              for (let x = 0; x < 32; x++) {
                const seed = (x * 73 + y * 31 + (x ^ y) * 7) % 100;
                const on = seed < 48 || ((x < 7 && y < 7) || (x > 24 && y < 7) || (x < 7 && y > 24));
                // finder pattern overrides
                const inFinder = (fx, fy) => x >= fx && x < fx+7 && y >= fy && y < fy+7;
                if (inFinder(0,0) || inFinder(25,0) || inFinder(0,25)) {
                  const innerX = x % 25, innerY = y % 25;
                  const xx = x - (x >= 25 ? 25 : 0);
                  const yy = y - (y >= 25 ? 25 : 0);
                  const edge = xx === 0 || xx === 6 || yy === 0 || yy === 6;
                  const center = xx >= 2 && xx <= 4 && yy >= 2 && yy <= 4;
                  if (edge || center) cells.push(<rect key={`${x}-${y}`} x={x} y={y} width="1" height="1" fill="#000" />);
                  continue;
                }
                if (on) cells.push(<rect key={`${x}-${y}`} x={x} y={y} width="1" height="1" fill="#000" />);
              }
            }
            return cells;
          })()}
        </svg>
      </div>
      <div style={{ fontFamily: "var(--font-mono)", fontSize: 22, fontWeight: 700, letterSpacing: ".18em" }}>{code}</div>
      <div style={{ textAlign: "center", marginTop: 6 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: "#000" }}>{locker}</div>
        <div style={{ fontSize: 12, color: "rgba(0,0,0,.7)", marginTop: 2 }}>{addr}</div>
      </div>
    </div>
  );
}

Object.assign(window, {
  MIcon, MobileHeader, MStatusChip, MLabel, MButton, ParcelRow, VTimeline, ScheduleOption, BottomNav, QRPanel,
  M_RED, M_YELLOW, M_GRAY100, M_GRAY150, M_GRAY200, M_GRAY300, M_GRAY500, M_GRAY600, M_GRAY800, M_FONT
});
