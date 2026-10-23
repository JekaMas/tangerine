export default function Icon({name, size=20, ...props}) {
  const paths = {
    library: <><path d="M4 4h6v16H4zM14 4h6v16h-6z"/><path d="M4 8h6m4 8h6"/></>,
    create: <><path d="M12 3v6m-3-3h6M5 12v8h14v-8M8 16h8"/><path d="m18 3 1 2 2 1-2 1-1 2-1-2-2-1 2-1z"/></>,
    attempts: <><path d="M8 4H5v17h14V4h-3M9 2h6v5H9zM8 12h8M8 16h5"/></>,
    audio: <><path d="M4 14v-3a8 8 0 0 1 16 0v3M4 12h3v8H4zM17 12h3v8h-3z"/></>,
    reports: <><path d="M4 3v17h17M8 16v-4m5 4V8m5 8V5"/></>,
    sources: <><path d="M3 6h7l2 3h9v11H3zM3 9h18"/></>,
    review: <><path d="M4 4h16v12H9l-5 4zM8 8h8M8 12h5"/></>,
    settings: <><path d="M4 7h16M4 17h16M8 4v6m8 4v6"/><circle cx="8" cy="7" r="2"/><circle cx="16" cy="17" r="2"/></>,
    recovery: <><path d="M4 9a8 8 0 1 1 0 7M4 4v5h5M12 7v5l3 2"/></>,
    cleanup: <><path d="M4 6h16M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7m4-7v7"/></>,
    arrow: <path d="M5 12h14m-5-5 5 5-5 5"/>,
    menu: <path d="M4 6h16M4 12h16M4 18h16"/>,
    close: <path d="m6 6 12 12M18 6 6 18"/>,
    search: <><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.library}</svg>;
}
