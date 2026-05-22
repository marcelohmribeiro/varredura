import { Navigate } from "react-router";
import useAuthStore from "src/store/authStore";

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated } = useAuthStore()
    
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />
    }

    return children
}

export default ProtectedRoute
export { ProtectedRoute }