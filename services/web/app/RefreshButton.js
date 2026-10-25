// Refresh reads remain keyboard reachable while another read/action is pending.
// Only an existing missing-record condition may make this action unavailable.
export default function RefreshButton({onClick, available=true, children='Refresh'}) {
  return <button type="button" className="secondary" disabled={!available} onClick={onClick}>{children}</button>;
}
