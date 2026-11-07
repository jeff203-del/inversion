import Script from "next/script";

export default function Home() {
  return <>
    <canvas id="static" aria-hidden="true" />
    <div className="app-shell">
      <aside className="rail">
        <a className="brand" href="#home" aria-label="Defend It home"><span className="brand-mark">D<span>.</span></span><span>defend<span className="muted">it</span></span></a>
        <div className="workspace-label">WORKSPACE <span>DEMO</span></div>
        <nav className="main-nav" aria-label="Main navigation">
          <button className="nav-item active" data-view="home"><span className="nav-icon">⌂</span>Overview</button>
          <button className="nav-item" data-view="campaigns"><span className="nav-icon">▤</span>Campaigns <i>2</i></button>
          <button className="nav-item" data-view="leaderboard"><span className="nav-icon">▥</span>Leaderboard</button>
          <button className="nav-item" data-view="evidence"><span className="nav-icon">⌕</span>Evidence board</button>
          <button className="nav-item" data-view="validation"><span className="nav-icon">⌁</span>Validation</button>
        </nav>
        <div className="rail-bottom"><div className="avatar">JM</div><div><b>Jeff Mutembei</b><small>Recruiter workspace</small></div><span className="dots">···</span></div>
      </aside>
      <main className="main">
        <header className="topbar"><div className="crumb"><span className="live-dot" /> ZINDUA SCHOOL <span className="slash">/</span> DEMO WORKSPACE</div><div className="top-actions"><span id="api-status" className="api-pill" title="Checking API connection">API · checking</span><span className="top-date">NOV 07, 2026</span><button id="launch-demo" className="button tiny">▶ &nbsp;Try candidate demo</button><button className="icon-btn" aria-label="Notifications">♧<em /></button><button className="avatar small">JM</button></div></header>
        <section id="view-home" className="view active" />
        <section id="view-campaigns" className="view" />
        <section id="view-leaderboard" className="view" />
        <section id="view-evidence" className="view" />
        <section id="view-validation" className="view" />
        <section id="view-defence" className="view" />
      </main>
    </div>
    <div id="toast" className="toast" role="status" aria-live="polite" />
    <Script src="/app.js" strategy="afterInteractive" />
  </>;
}
