import csv
import re
import dns.resolver
import smtplib
import socket
import tkinter as tk
from tkinter import filedialog

def is_valid_email(email):
    # Regulärer Ausdruck zur Überprüfung der E-Mail-Syntax
    email_regex = r'^[\w\.-]+@[\w\.-]+$'
    return re.match(email_regex, email) is not None

def check_mx_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        if answers:
            mx_records = [rdata.exchange.to_text() for rdata in answers]
            return mx_records
        else:
            return []
    except dns.resolver.NXDOMAIN:
        return []
    except Exception as e:
        print(f"Fehler bei der MX-Abfrage für {domain}: {e}")
        return []

def has_mx_records(domain):
    mx_records = check_mx_records(domain)
    return bool(mx_records)

def email_exists(email):
    if not is_valid_email(email):
        return "No"  # E-Mail hat falsche Syntax
    domain = email.split('@')[1]
    mx_records = check_mx_records(domain)
    if mx_records:
        try:
            host = socket.gethostname()
            server = smtplib.SMTP()
            server.set_debuglevel(1)  # Debugging auf Level 1 erhöhen
            server.connect(mx_records[0])
            server.helo(host)
            server.mail('me@domain.com')
            code, message = server.rcpt(str(email))
            server.quit()
            if code == 250:
                return "Yes"
            else:
                return "No"
        except smtplib.SMTPServerDisconnected:
            return "No"
        except smtplib.SMTPRecipientsRefused:
            return "No"
        except Exception as e:
            print(f"Fehler bei der SMTP-Verifikation für {email}: {e}")
            return "No"
    else:
        return "No"

def process_csv(input_filename, output_filename):
    with open(input_filename, 'r', newline='') as infile, open(output_filename, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Email_exists"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            email = row["Email"]
            row["Email_exists"] = email_exists(email)
            writer.writerow(row)

def browse_file():
    input_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if input_file:
        output_file = "output.csv"  # Hier kannst du den Namen der Ausgabedatei anpassen
        process_csv(input_file, output_file)
        result_label.config(text="Verarbeitung abgeschlossen.")

# GUI erstellen
root = tk.Tk()
root.title("CSV-Verarbeitung")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

browse_button = tk.Button(frame, text="CSV-Datei auswählen", command=browse_file)
browse_button.pack()

result_label = tk.Label(frame, text="")
result_label.pack()

root.mainloop()
