const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('--- [AgriSense AI / BT195] Vercel Production Build Started ---');

// 1. Build React dashboard
console.log('[1/3] Building React analytics dashboard...');
execSync('npm --prefix frontend install --legacy-peer-deps', { stdio: 'inherit' });
execSync('npm --prefix frontend run build', { stdio: 'inherit' });

// 2. Prepare unified public distribution folder
console.log('[2/3] Assembling public deployment artifacts...');
const publicDir = path.join(__dirname, 'public');
const dashboardDir = path.join(publicDir, 'dashboard');
const assetsDir = path.join(publicDir, 'assets');

if (!fs.existsSync(publicDir)) {
  fs.mkdirSync(publicDir, { recursive: true });
}

// Copy landing page
fs.copyFileSync(path.join(__dirname, 'index.html'), path.join(publicDir, 'index.html'));
console.log(' -> Copied index.html to public/index.html');

// Copy landing page assets
if (fs.existsSync(path.join(__dirname, 'assets'))) {
  fs.cpSync(path.join(__dirname, 'assets'), assetsDir, { recursive: true });
  console.log(' -> Copied assets/ to public/assets/');
}

// Copy built React application to public/dashboard
const frontendDist = path.join(__dirname, 'frontend', 'dist');
if (fs.existsSync(frontendDist)) {
  fs.cpSync(frontendDist, dashboardDir, { recursive: true });
  console.log(' -> Copied frontend/dist/ to public/dashboard/');
}

console.log('[3/3] Build completed successfully. Output ready for Vercel deployment.');
