/**
 * Vendor Dashboard - Placeholder
 */

import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const VendorDashboard = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box>
        <Typography variant="h4">Vendor Dashboard</Typography>
        <Typography variant="body1">
          Vendor dashboard implementation - View available jobs, manage estimates, track completed work
        </Typography>
      </Box>
    </Container>
  );
};

export default VendorDashboard;
