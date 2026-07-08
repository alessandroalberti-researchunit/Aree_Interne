/* Foreseen carousel — interactive viewer (UI kit index app). */
const { IconButton, Button, Badge } = window.IZILabDesignSystem_03588f;
const SLIDES = window.IZI_FORESEEN.slides;

const SLIDE_W = 1080, SLIDE_H = 1350, DISPLAY_W = 408;
const SCALE = DISPLAY_W / SLIDE_W;

function ScaledSlide({ data }) {
  return (
    <div style={{ width: DISPLAY_W, height: SLIDE_H * SCALE, borderRadius: 22, overflow: "hidden", border: "1px solid var(--border-default)", boxShadow: "var(--glow-violet)", flex: "none" }}>
      <div style={{ width: SLIDE_W, height: SLIDE_H, transform: `scale(${SCALE})`, transformOrigin: "top left" }}>
        <window.CarouselSlide data={data} />
      </div>
    </div>
  );
}

function Thumb({ data, active, onClick, index }) {
  const tw = 76, ts = tw / SLIDE_W;
  return (
    <button onClick={onClick} aria-label={`Slide ${index + 1}`}
      style={{ all: "unset", cursor: "pointer", width: tw, height: SLIDE_H * ts, borderRadius: 8, overflow: "hidden",
        outline: active ? "2px solid var(--color-accent)" : "1px solid var(--border-default)",
        outlineOffset: active ? 1 : 0, flex: "none", transition: "outline-color var(--dur-fast)" }}>
      <div style={{ width: SLIDE_W, height: SLIDE_H, transform: `scale(${ts})`, transformOrigin: "top left" }}>
        <window.CarouselSlide data={data} />
      </div>
    </button>
  );
}

function App() {
  const [i, setI] = React.useState(0);
  const go = (n) => setI((p) => (n + SLIDES.length) % SLIDES.length);

  React.useEffect(() => {
    const onKey = (e) => { if (e.key === "ArrowRight") go(i + 1); if (e.key === "ArrowLeft") go(i - 1); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-page)", color: "var(--text-body)", fontFamily: "var(--font-body)", display: "flex", flexDirection: "column" }}>
      {/* top bar */}
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "20px 32px", borderBottom: "1px solid var(--border-subtle)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ background: "#FDFDFF", borderRadius: 8, padding: "6px 10px", display: "flex" }}>
            <img src="../../assets/logo/logo-izilab.png" alt="IZILab" style={{ height: 20 }} />
          </div>
          <span style={{ fontFamily: "var(--font-display)", fontSize: 22, color: "var(--text-heading)" }}>Foreseen</span>
          <Badge tone="accent" variant="soft">Carousel</Badge>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <Button variant="secondary" size="sm">Modifica</Button>
          <Button variant="primary" size="sm" iconRight={<span>&rarr;</span>}>Pubblica</Button>
        </div>
      </header>

      {/* stage */}
      <main style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 28, padding: "40px 24px" }}>
        <IconButton variant="outline" label="Precedente" onClick={() => go(i - 1)}>‹</IconButton>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 20 }}>
          <ScaledSlide data={SLIDES[i]} />
          {/* dots */}
          <div style={{ display: "flex", gap: 8 }}>
            {SLIDES.map((_, k) => (
              <span key={k} onClick={() => go(k)} style={{ width: k === i ? 22 : 8, height: 8, borderRadius: 999, cursor: "pointer",
                background: k === i ? "var(--color-accent)" : "var(--surface-raised)", border: "1px solid var(--border-default)", transition: "width var(--dur-base) var(--ease-emphasis)" }} />
            ))}
          </div>
        </div>
        <IconButton variant="outline" label="Successivo" onClick={() => go(i + 1)}>›</IconButton>
      </main>

      {/* thumbnail rail */}
      <footer style={{ borderTop: "1px solid var(--border-subtle)", padding: "16px 32px", display: "flex", alignItems: "center", gap: 18 }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-muted)", flex: "none" }}>
          {String(i + 1).padStart(2, "0")} / {String(SLIDES.length).padStart(2, "0")}
        </span>
        <div style={{ display: "flex", gap: 10, overflowX: "auto", paddingBottom: 4 }}>
          {SLIDES.map((s, k) => (
            <Thumb key={k} data={s} index={k} active={k === i} onClick={() => go(k)} />
          ))}
        </div>
      </footer>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
