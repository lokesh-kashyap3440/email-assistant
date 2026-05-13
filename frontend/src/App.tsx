import { useState } from 'react'
import { Navbar } from './components/Navbar'
import { InboxView } from './components/InboxView'
import { ConfigView } from './components/ConfigView'
import { SetupView } from './components/SetupView'

type Page = 'inbox' | 'config' | 'setup'

function App() {
  const [page, setPage] = useState<Page>('inbox')

  return (
    <div className="flex h-screen bg-gray-950">
      <Navbar currentPage={page} onNavigate={setPage} />
      <main className="flex-1 overflow-y-auto p-8">
        {page === 'inbox' && <InboxView />}
        {page === 'config' && <ConfigView />}
        {page === 'setup' && <SetupView />}
      </main>
    </div>
  )
}

export default App
