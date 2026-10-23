'use client';
import {useState} from 'react';
import {usePathname} from 'next/navigation';
import Icon from './Icon';

const groups = [
  {label:'Practice', links:[['/','Library','library'],['/prepare','New exercise','create'],['/attempts','Saved attempts','attempts'],['/audio','Saved audio','audio']]},
  {label:'Explore', links:[['/reviews','LLM reviews','review'],['/reports','Reports and experiments','reports'],['/sources','Source library','sources']]},
  {label:'Workspace', links:[['/settings','Settings','settings'],['/recovery','Recovery','recovery'],['/cleanup','Storage cleanup','cleanup']]},
];
export default function AppShell({children}) {
  const path=usePathname(), [open,setOpen]=useState(false);
  const activePath=path==='/listen'?'/':path;
  return <div className="app-shell">
    <a className="skip-link" href="#main-content">Skip to content</a>
    <aside className={'sidebar'+(open?' is-open':'')}>
      <div className="sidebar-top"><a className="brand" href="/" aria-label="Tangerine home">
        <svg className="brand-fruit" width="35" height="38" viewBox="0 0 35 38" aria-hidden="true"><path d="M18 9c0-5 5-8 10-6-1 5-5 7-10 6" fill="#496F48"/><path d="M17 7v6" stroke="#496F48" strokeWidth="2"/><path d="M31 23c0 8-6 13-14 13S3 31 3 23s6-13 14-13 14 5 14 13" fill="#F27832"/><path d="M10 18c-2 2-3 4-3 7" fill="none" stroke="#FFD3AD" strokeWidth="2.5" strokeLinecap="round"/></svg>
        <span>Tangerine<small>Listen. Notice. Learn.</small></span>
      </a><button type="button" className="menu-toggle secondary" aria-label="Toggle navigation" aria-expanded={open} aria-controls="workspace-navigation" onClick={()=>setOpen(!open)}><Icon name={open?'close':'menu'}/></button></div>
      <nav id="workspace-navigation" aria-label="Workspace navigation" className="workspace-navigation">
        {groups.map(group=><div className="nav-group" key={group.label}><p>{group.label}</p>{group.links.map(([href,label,icon])=><a key={href} href={href} aria-current={activePath===href?'page':undefined} onClick={()=>setOpen(false)}><Icon name={icon}/><span>{label}</span></a>)}</div>)}
      </nav>
      <div className="workspace-note"><span className="local-dot"/><div>Local workspace<small>Saved on this computer.</small></div></div>
    </aside>
    <div className="workspace-content">{children}</div>
  </div>;
}
