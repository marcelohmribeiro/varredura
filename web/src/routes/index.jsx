import { createBrowserRouter } from "react-router";
import Layout from "src/pages/layout";
import Authlayout from "src/pages/auth/layout";
import Index from "src/pages";
import Login from "src/pages/(public)/login";
import Dashboard from "src/pages/auth/dashboard";

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Index />, },
      {
        path: 'login',
        element: <Login />,
      },
      {
        path: 'auth',
        element: <Authlayout />,
        children: [
          {
            path: 'dashboard',
            element: <Dashboard />,
          },
          {
            path: 'configuracoes',
            element: <h1>Configurações</h1>,
          }
        ]
      }
    ]
  }
])
