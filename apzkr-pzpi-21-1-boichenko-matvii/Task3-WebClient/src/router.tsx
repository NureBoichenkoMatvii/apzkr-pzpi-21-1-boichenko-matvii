import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom';
import React, { Suspense } from 'react';
import { Main } from '@pages/Main';
import Login from "@pages/Auth/Login";
import Medicines from "@pages/Medicines.tsx";
import Register from "@pages/Auth/Register";
import Profile from "@pages/Profile";
import Cart from "@pages/Cart";
import ProfileOrders from "@pages/ProfileOrders";
// import DelivererMachines from "@pages/DelivererMachines";
// import DelivererMachineDetail from "@pages/DelivererMachineDetail";
// import Statistics from "@pages/Statistics";
import NotFound from "@pages/NotFound";
import Home from "@pages/Home.tsx";

const router = createBrowserRouter(
  [{
    path: '/',
    element: (<Suspense fallback={<>Loading...</>}> <Outlet /> </Suspense>),
    errorElement: (<h1>ERROR</h1>),
    children: [
      {
        element: <Main />,
        children: [
          {index: true, element: <Home />},
          {path: '/home', element: <Home />},
          {path: '/medicines', element: <Medicines />},
          {path: '/login', element: <Login />},
          {path: '/register', element: <Register />},
          {path: '/card', element: <Cart />},
          {path: '/profile', element: <Profile />},
          {path: '/profile/orders', element: <ProfileOrders />},
          // {path: '/deliverer/machines', element: <DelivererMachines />},
          // {path: '/deliverer/machines/:id', element: <DelivererMachineDetail />},
          // {path: '/deliverer/statistics', element: <Statistics />},
          {path: '/404', element: <NotFound />},
          {
            path: '*', element: <Navigate to={'/404'} />
          },
        ]
      },
    ]
  }]
)

export { router as Router }