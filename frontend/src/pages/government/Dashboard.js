/**
 * Government Dashboard - Placeholder
 */

import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const GovernmentDashboard = () => {
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box>
        <Typography variant="h4">Government Dashboard</Typography>
        <Typography variant="body1">
          Government dashboard implementation - Manage assigned complaints, track resolution, view statistics
        </Typography>
      </Box>
    </Container>
  );
};

export default GovernmentDashboard;
