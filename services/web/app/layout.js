import './style.css';
import AppShell from './AppShell';
export const metadata = { title: 'Tangerine · Teacher Error Trainer', description: 'Practice noticing and explaining learner errors.' };
export default function RootLayout({ children }) {
  return <html lang="en"><body><AppShell>{children}</AppShell></body></html>;
}
