import React from 'react';
import { Typography } from '@mui/material';

const DataInventory = () => {
  return (
    <div>
      <Typography variant="h4" component="h1" gutterBottom>
        Data Inventory
      </Typography>
      <Typography variant="body1">
        This page will allow you to manage your data categories and storage locations.
      </Typography>
    </div>
  );
};

export default DataInventory;