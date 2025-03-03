import React from 'react';
import { 
  AppBar, Toolbar, Typography, Container, Box, 
  Drawer, List, ListItem, ListItemIcon, ListItemText, 
  Divider, IconButton
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  Storage as StorageIcon,
  Assignment as AssignmentIcon,
  Description as DescriptionIcon,
  Menu as MenuIcon
} from '@mui/icons-material';
import { Link } from 'react-router-dom';

const Layout = ({ children }) => {
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'Data Inventory', icon: <StorageIcon />, path: '/data-inventory' },
    { text: 'Subject Requests', icon: <AssignmentIcon />, path: '/subject-requests' },
    { text: 'Documents', icon: <DescriptionIcon />, path: '/documents' },
  ];

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed">
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={toggleDrawer}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            GDPR Compliance Manager
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={toggleDrawer}
        sx={{
          width: 240,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {menuItems.map((item) => (
              <ListItem button key={item.text} component={Link} to={item.path} onClick={toggleDrawer}>
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItem>
            ))}
          </List>
          <Divider />
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar /> {/* This creates space below the AppBar */}
        <Container maxWidth="lg">
          {children}
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;