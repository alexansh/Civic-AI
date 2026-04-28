import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button, Container, Typography, Box, Paper } from '@mui/material';

const RoleSelection = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleRoleSelect = (role) => {
    navigate(`/${role}/dashboard`);
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            Welcome, {user?.name || 'User'}
          </Typography>
          <Typography variant="h6" gutterBottom>
            Select your role
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 4 }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={() => handleRoleSelect('citizen')}
            >
              Citizen
            </Button>
            <Button
              variant="contained"
              color="secondary"
              size="large"
              onClick={() => handleRoleSelect('vendor')}
            >
              Vendor
            </Button>
            <Button
              variant="contained"
              color="info"
              size="large"
              onClick={() => handleRoleSelect('government')}
            >
              Government
            </Button>
            {user?.role === 'admin' && (
              <Button
                variant="contained"
                color="error"
                size="large"
                onClick={() => handleRoleSelect('admin')}
              >
                Admin
              </Button>
            )}
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default RoleSelection;