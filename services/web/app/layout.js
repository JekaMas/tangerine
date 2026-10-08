import './style.css';
export const metadata = { title: 'Tangerine · Teacher Error Trainer', description: 'Practice noticing and explaining learner errors.' };
export default function RootLayout({ children }) {
  return <html lang="en"><body>{children}</body></html>;
}
