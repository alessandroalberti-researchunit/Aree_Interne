/* Foreseen carousel — a single 4:5 social slide (faithful recreation). */
function CarouselSlide({ data }) {
  const dark = data.theme === "dark";
  const c = dark
    ? { kicker: "var(--violet-300)", title: "var(--aqua-200)", body: "var(--blanche-400)", base: "#0F0830" }
    : { kicker: "#575767", title: "#541BC6", body: "#272735", base: "#FBFBFF" };

  const bgStyle = data.bg
    ? { backgroundImage: `url(${data.bg})`, backgroundSize: "cover", backgroundPosition: "center" }
    : { background: c.base };

  return (
    <div style={{ position: "relative", width: "100%", height: "100%", overflow: "hidden", ...bgStyle, color: c.body, fontFamily: "var(--font-body)" }}>
      {/* dark overlay for legibility on image bgs */}
      {data.bg && dark && (
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(15,8,48,0.35) 0%, rgba(15,8,48,0.78) 100%)" }} />
      )}

      {/* logo top-right — protected in a light chip on dark slides */}
      <div style={{ position: "absolute", top: 36, right: 40, zIndex: 2, display: "flex", alignItems: "center",
        background: dark ? "#FDFDFF" : "transparent", padding: dark ? "8px 12px" : 0, borderRadius: dark ? 10 : 0 }}>
        <img src="../../assets/logo/logo-izilab.png" alt="IZILab" style={{ height: dark ? 26 : 30 }} />
      </div>

      {data.type === "cover" ? (
        <div style={{ position: "absolute", inset: 0, zIndex: 2, padding: "0 56px 64px", display: "flex", flexDirection: "column", justifyContent: "flex-end" }}>
          <h1 style={{ fontFamily: "var(--font-display)", fontWeight: 500, fontSize: 92, lineHeight: 0.98, letterSpacing: "-0.02em", margin: 0, color: c.title }}>
            {data.title}
          </h1>
          <div style={{ width: 56, height: 4, background: "var(--color-accent)", borderRadius: 999, margin: "28px 0" }} />
          <p style={{ fontSize: 26, lineHeight: 1.35, margin: 0, whiteSpace: "pre-line", color: c.body }}>{data.subtitle}</p>
          <div style={{ marginTop: 48, fontSize: 40, color: "var(--color-accent)" }}>&rarr;</div>
        </div>
      ) : (
        <div style={{ position: "absolute", inset: 0, zIndex: 2, padding: 56, display: "flex", flexDirection: "column" }}>
          <div style={{ fontSize: 18, fontWeight: 600, letterSpacing: "0.14em", textTransform: "uppercase", color: c.kicker }}>
            {data.kicker}
          </div>
          <h2 style={{ fontFamily: "var(--font-display)", fontWeight: 500, fontSize: 56, lineHeight: 1.04, letterSpacing: "-0.015em", margin: "28px 0 0", color: c.title, maxWidth: "13ch" }}>
            {data.title}
          </h2>
          <div style={{ width: 48, height: 4, background: "var(--color-accent)", borderRadius: 999, margin: "32px 0" }} />
          <p style={{ fontSize: 23, lineHeight: 1.5, margin: 0, maxWidth: "26ch", color: c.body }}>{data.body}</p>
          <div style={{ marginTop: "auto", display: "flex", alignItems: "center", gap: 14 }}>
            <div style={{ flex: 1, height: 2, background: dark ? "rgba(236,236,255,0.18)" : "rgba(39,39,53,0.14)" }} />
            <span style={{ fontSize: 34, color: "var(--color-accent)" }}>&rarr;</span>
          </div>
        </div>
      )}
    </div>
  );
}
window.CarouselSlide = CarouselSlide;
