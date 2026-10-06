import { Link, useLocation } from 'react-router-dom'
import { cn } from 'src/lib/utils'
import { Settings, ChevronLeft } from 'lucide-react'
import { Button } from 'src/components/ui/button'
import { navigation } from 'src/constants'
import icone from 'src/assets/icone.png'

export function Sidebar({ collapsed, onToggle, mobileOpen, onMobileClose }) {
	const location = useLocation()

	const sidebarContent = (
		<>
			{/* Header */}
			<div className='flex h-16 items-center justify-between border-b px-4'>
				{!collapsed && (
					<div className='flex items-center gap-2'>
						<img src={icone} alt='Logo' className='h-8 w-8 rounded-md' />
						<div className='flex flex-col'>
							<span className='text-sm font-semibold'>Varredura</span>
						</div>
					</div>
				)}
				<Button
					variant='ghost'
					size='icon'
					onClick={onToggle}
					className={cn('hidden h-8 w-8 md:inline-flex', collapsed && 'mx-auto')}
				>
					<ChevronLeft className={cn('h-4 w-4 transition-transform', collapsed && 'rotate-180')} />
				</Button>
			</div>

			{/* Navigation */}
			<nav className='space-y-1 p-2'>
				{navigation
					.map((item) => {
						const Icon = item.icon
						const isActive = location.pathname === item.href

						return (
							<Link
								key={item.href}
								to={item.href}
								onClick={onMobileClose}
								className={cn(
									'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
									isActive
										? 'bg-primary text-primary-foreground'
										: 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
									collapsed && 'md:justify-center'
								)}
							>
								<Icon className='h-5 w-5 shrink-0' />
								{(!collapsed || mobileOpen) && <span>{item.title}</span>}
							</Link>
						)
					})}
			</nav>

			{/* Footer */}
			<div className='absolute bottom-0 w-full border-t p-2'>
				<Link
					to='/auth/configuracoes'
					onClick={onMobileClose}
					className={cn(
						'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground',
						collapsed && 'md:justify-center'
					)}
				>
					<Settings className='h-5 w-5 shrink-0' />
					{(!collapsed || mobileOpen) && <span>Configurações</span>}
				</Link>
			</div>
		</>
	)

	return (
		<>
			{/* Sidebar */}
			<aside
				className={cn(
					'fixed left-0 top-0 z-40 hidden h-screen border-r bg-card transition-all duration-300 md:block',
					collapsed ? 'w-16' : 'w-64'
				)}
			>
				{sidebarContent}
			</aside>
		</>
	)
}
