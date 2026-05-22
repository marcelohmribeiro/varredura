import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { ProtectedRoute } from 'src/components/_protected-route'
import { Sidebar } from 'src/pages/components'
import { cn } from 'src/lib/utils'

export default function Layout() {
	const [collapsed, setCollapsed] = useState(false)
	const [mobileOpen, setMobileOpen] = useState(false)

	return (
		<ProtectedRoute>
			<div className='flex h-screen w-full overflow-hidden bg-background'>
				<Sidebar
					collapsed={collapsed}
					onToggle={() => setCollapsed(!collapsed)}
					mobileOpen={mobileOpen}
					onMobileClose={() => setMobileOpen(false)}
				/>

				<div
					className={cn(
						'flex flex-1 flex-col overflow-hidden transition-all duration-300',
						'pl-0 md:pl-64',
						collapsed && 'md:pl-16'
					)}
				>
					<main className='flex-1 overflow-y-auto p-4 md:p-6'>
						<Outlet />
					</main>
				</div>
			</div>
		</ProtectedRoute>
	)
}
