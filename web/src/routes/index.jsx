import { createBrowserRouter } from "react-router";
import Layout from "src/pages/layout";
import Authlayout from "src/pages/auth/layout";
import Index from "src/pages";
import Login from "src/pages/(public)/login";
import Dashboard from "src/pages/auth/dashboard";
import Scraping from "src/pages/auth/scrapping";
import Configuracoes from "src/pages/auth/configuracoes";

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
            path: 'scraping',
            element: <Scraping />,
          },
          {
            path: 'configuracoes',
            element: <Configuracoes />,
          }
        ]
      }
    ]
  }
])
