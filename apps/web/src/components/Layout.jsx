import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import Sidebar from './Sidebar';
import Header from './Header';

const Layout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Sidebar 
        mobileOpen={mobileOpen} 
        handleDrawerToggle={handleDrawerToggle}
        isMobile={isMobile}
      />
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          width: { sm: `calc(100% - 240px)` },
          height: '100vh',
          overflow: 'auto',
          backgroundColor: 'background.default'
        }}
      >
        <Header handleDrawerToggle={handleDrawerToggle} />
        <Box sx={{ mt: 8, py: 2 }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;
