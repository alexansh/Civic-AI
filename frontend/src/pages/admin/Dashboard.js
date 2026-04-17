/**
 * Admin Dashboard - Placeholder
 */

import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const AdminDashboard = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box>
        <Typography variant="h4">Admin Dashboard</Typography>
        <Typography variant="body1">
          Admin dashboard implementation - Manage users, vendors, government bodies, view platform statistics
        </Typography>
      </Box>
    </Container>
  );
};

export default AdminDashboard;
