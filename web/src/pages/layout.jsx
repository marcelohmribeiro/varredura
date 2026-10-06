import { Outlet } from 'react-router-dom'

export default function Layout() {		
	return (
		<div className='flex min-h-screen w-full overflow-hidden bg-background'>
			<Outlet />
		</div>
	)
}
