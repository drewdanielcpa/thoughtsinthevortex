@echo off
title Build 2,086 Privacy-Screened Subfile Vault Pages (thoughtsinthevortex.com)
echo ============================================================================
echo Rendering ^& Privacy-Screening NORJAK Subfile Vault Pages (.webp)...
echo (Auto-detects your local FBI Vault PDFs and word_positions archives)
echo ============================================================================
python "%~dp0build_subfile_vault_pages.py"
echo.
echo Done! Review PRIVACY_BLACKOUT_AUDIT_SHEET.jpg if desired, then run
echo 2_PUBLISH_SITE_TO_GITHUB.bat to push live to thoughtsinthevortex.com.
echo.
pause
