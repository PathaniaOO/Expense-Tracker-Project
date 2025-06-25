import argparse
import logging
import schedule
import time
from .logic import insert_transaction, fetch_monthly_summary, plot_summary, fetch_all_transactions
from .db import create_table

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scheduled_report():
    logging.info("Running scheduled report generation...")
    summary = fetch_monthly_summary()
    if summary.empty:
        logging.info("No transactions to report.")
        return
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    export_path = f"monthly_summary_{timestamp}.csv"
    summary.to_csv(export_path)
    logging.info(f"Report saved to {export_path}")
    plot_summary(summary)

def main():
    parser = argparse.ArgumentParser(description="Financial Expense Tracker CLI")
    parser.add_argument('--add', nargs=5, metavar=('DATE', 'TYPE', 'CATEGORY', 'AMOUNT', 'DESCRIPTION'),
                        help="Add a transaction. Example: --add 2025-06-20 expense Food 100 'Lunch'")
    parser.add_argument('--summary', action='store_true', help="Print monthly summary report")
    parser.add_argument('--export', metavar='FILENAME', help="Export monthly summary to CSV")
    parser.add_argument('--plot', action='store_true', help="Plot the monthly summary")
    parser.add_argument('--schedule-report', action='store_true', help="Run scheduled monthly report every minute")
    parser.add_argument('--list', action='store_true', help="List all transactions")

    args = parser.parse_args()
    create_table()

    if args.add:
        date, ttype, category, amount_str, description = args.add
        try:
            amount = float(amount_str)
        except ValueError:
            logging.error("Amount must be a number.")
            return
        insert_transaction(date, ttype, category, amount, description)

    if args.summary or args.export or args.plot:
        summary = fetch_monthly_summary()
        if summary.empty:
            logging.info("No data available.")
            return
        print(summary)
        if args.export:
            summary.to_csv(args.export)
            logging.info(f"Summary exported to {args.export}")
        if args.plot:
            plot_summary(summary)

    if args.list:
        df = fetch_all_transactions()
        print(df)

    if args.schedule_report:
        schedule.every(1).minutes.do(scheduled_report)
        logging.info("Scheduled report generation started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Scheduled report generation stopped.")

if __name__ == "__main__":
    main()