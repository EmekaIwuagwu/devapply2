"""
Email Notification Service — sends job run summary emails after agent completes.
Uses SMTP (works with Gmail, Outlook, any provider).

To enable: set EMAIL_SENDER, EMAIL_PASSWORD in .env
For Gmail: create an App Password at https://myaccount.google.com/apppasswords
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def _get_email_config():
    """Read email config from environment."""
    import os
    return {
        "sender": os.getenv("EMAIL_SENDER", ""),
        "password": os.getenv("EMAIL_PASSWORD", ""),
        "smtp_host": os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
        "enabled": os.getenv("EMAIL_ENABLED", "false").lower() == "true",
    }


def _build_html_email(
    recipient_email: str,
    jobs_found: int,
    jobs_applied: List[Dict],
    jobs_searched: List[Dict],
    strategy_name: str,
    run_date: str,
) -> str:
    """Build a beautiful HTML email report."""

    applied_rows = ""
    for job in jobs_applied:
        score = job.get("match_score", 0)
        score_color = "#4ade80" if score >= 80 else "#facc15" if score >= 60 else "#f87171"
        applied_rows += f"""
        <tr>
            <td style="padding:10px 12px; border-bottom:1px solid #2d2d2d;">
                <b>{job.get('title','')}</b><br>
                <span style="color:#9ca3af; font-size:12px;">{job.get('company','')}</span>
            </td>
            <td style="padding:10px 12px; border-bottom:1px solid #2d2d2d; color:#9ca3af;">{job.get('platform','')}</td>
            <td style="padding:10px 12px; border-bottom:1px solid #2d2d2d;">
                <span style="color:{score_color}; font-weight:600;">{score}/100</span>
            </td>
            <td style="padding:10px 12px; border-bottom:1px solid #2d2d2d;">
                <a href="{job.get('url','#')}" style="color:#8b5cf6; text-decoration:none;">View Job →</a>
            </td>
        </tr>
        """

    searched_list = ""
    for job in jobs_searched[:15]:
        searched_list += f"""
        <li style="padding:6px 0; border-bottom:1px solid #2d2d2d; color:#d1d5db;">
            <b>{job.get('title','')}</b> — {job.get('company','')}
            <span style="color:#9ca3af; font-size:12px;"> ({job.get('platform','')})</span>
        </li>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:0; background:#0f0f0f; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color:#e5e7eb;">
        <div style="max-width:620px; margin:32px auto; background:#1a1a2e; border-radius:16px; overflow:hidden; border:1px solid #2d2d2d;">

            <!-- Header -->
            <div style="background:linear-gradient(135deg, #7c3aed, #3b82f6); padding:32px;">
                <h1 style="margin:0; color:#fff; font-size:24px;">🚀 DevApply Run Complete</h1>
                <p style="margin:8px 0 0; color:rgba(255,255,255,0.8);">{run_date} · Strategy: <b>{strategy_name}</b></p>
            </div>

            <!-- Stats row -->
            <div style="display:flex; padding:24px; gap:16px;">
                <div style="flex:1; background:#0d1117; border-radius:10px; padding:16px; text-align:center; border:1px solid #2d2d2d;">
                    <div style="font-size:32px; font-weight:700; color:#8b5cf6;">{jobs_found}</div>
                    <div style="color:#9ca3af; font-size:13px;">Jobs Found</div>
                </div>
                <div style="flex:1; background:#0d1117; border-radius:10px; padding:16px; text-align:center; border:1px solid #2d2d2d;">
                    <div style="font-size:32px; font-weight:700; color:#4ade80;">{len(jobs_applied)}</div>
                    <div style="color:#9ca3af; font-size:13px;">Top Matches Queued</div>
                </div>
                <div style="flex:1; background:#0d1117; border-radius:10px; padding:16px; text-align:center; border:1px solid #2d2d2d;">
                    <div style="font-size:32px; font-weight:700; color:#60a5fa;">{len(jobs_searched)}</div>
                    <div style="color:#9ca3af; font-size:13px;">Total Scanned</div>
                </div>
            </div>

            <!-- Top matches applied -->
            {'<div style="padding:0 24px 24px;"><h2 style="color:#e5e7eb; font-size:16px; margin-bottom:12px;">🎯 Top Matches Identified</h2><table style="width:100%; border-collapse:collapse; background:#0d1117; border-radius:10px; overflow:hidden; border:1px solid #2d2d2d;"><thead><tr style="background:#161b22;"><th style="padding:10px 12px; text-align:left; color:#9ca3af; font-size:12px; font-weight:600;">ROLE</th><th style="padding:10px 12px; text-align:left; color:#9ca3af; font-size:12px; font-weight:600;">SOURCE</th><th style="padding:10px 12px; text-align:left; color:#9ca3af; font-size:12px; font-weight:600;">SCORE</th><th style="padding:10px 12px; text-align:left; color:#9ca3af; font-size:12px; font-weight:600;">LINK</th></tr></thead><tbody>' + applied_rows + '</tbody></table></div>' if jobs_applied else ''}

            <!-- All jobs scanned -->
            <div style="padding:0 24px 24px;">
                <h2 style="color:#e5e7eb; font-size:16px; margin-bottom:12px;">📋 All Jobs Scanned This Run</h2>
                <ul style="list-style:none; margin:0; padding:0; background:#0d1117; border-radius:10px; border:1px solid #2d2d2d; padding:12px 16px;">
                    {searched_list if searched_list else '<li style="color:#9ca3af;">No jobs found this run.</li>'}
                </ul>
            </div>

            <!-- Note -->
            <div style="padding:16px 24px 32px;">
                <div style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.3); border-radius:8px; padding:14px; font-size:13px; color:#93c5fd;">
                    ⚠️ <b>Note:</b> DevApply has <b>identified</b> these matches. 
                    Full automated form submission requires Playwright browser automation to be enabled and your profile to be fully set up.
                    Review these jobs on your <a href="http://localhost:8501/Applications" style="color:#60a5fa;">Applications page</a>.
                </div>
            </div>

            <!-- Footer -->
            <div style="background:#0d1117; padding:16px 24px; text-align:center; color:#4b5563; font-size:12px; border-top:1px solid #2d2d2d;">
                DevApply v1.0 · Autonomous Job Application Agent
            </div>
        </div>
    </body>
    </html>
    """


def send_run_summary_email(
    recipient_email: str,
    strategy_name: str,
    jobs_found: int,
    jobs_applied: List[Dict],
    jobs_searched: List[Dict],
) -> bool:
    """
    Send a job run summary email to the user.
    Returns True if sent successfully, False otherwise.
    """
    config = _get_email_config()

    if not config["enabled"]:
        logger.info("Email notifications disabled — set EMAIL_ENABLED=true in .env to enable")
        return False

    if not config["sender"] or not config["password"]:
        logger.warning("Email not configured — set EMAIL_SENDER and EMAIL_PASSWORD in .env")
        return False

    run_date = datetime.now().strftime("%B %d, %Y at %H:%M")
    subject = f"[DevApply] Run Complete — {jobs_found} jobs found · {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"DevApply <{config['sender']}>"
        msg["To"] = recipient_email

        # Plain text fallback
        plain = (
            f"DevApply Run Complete\n"
            f"Strategy: {strategy_name}\n"
            f"Date: {run_date}\n"
            f"Jobs found: {jobs_found}\n"
            f"Top matches: {len(jobs_applied)}\n\n"
            + "\n".join([f"- {j.get('title','')} @ {j.get('company','')} ({j.get('platform','')})" for j in jobs_applied])
        )
        msg.attach(MIMEText(plain, "plain"))

        # HTML version
        html = _build_html_email(
            recipient_email=recipient_email,
            jobs_found=jobs_found,
            jobs_applied=jobs_applied,
            jobs_searched=jobs_searched,
            strategy_name=strategy_name,
            run_date=run_date,
        )
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(config["sender"], config["password"])
            smtp.sendmail(config["sender"], recipient_email, msg.as_string())

        logger.info(f"✅ Summary email sent to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
