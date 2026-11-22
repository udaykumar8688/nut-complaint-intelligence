# NUT Complaint Intelligence

## What this project is about

NUT is a college group project created by **Nishant Kumar, Uday Kumar, and Tanu Yadav**. It explores how Natural Language Processing can help companies handle customer complaints more efficiently.

Customers usually explain their issue in their own words. A company may receive hundreds of these messages, and manually deciding which department should receive each message can be slow. A billing issue sent to technical support, for example, creates unnecessary delay for the customer.

## What NUT does

NUT reads a written customer complaint and recommends one of six support routes:

- **Billing** for charges, refunds, invoices, payments, and subscription issues.
- **Customer Service** for delayed responses, account help, communication, and escalation requests.
- **Technical Support** for app errors, login problems, device issues, and system failures.
- **Account Management** for profile, ownership, administrator, and settings changes.
- **Security & Fraud** for suspicious activity, unauthorized access, and scam reports.
- **Orders & Delivery** for packages, tracking, returns, and delivery issues.

The project also shows a confidence score and the important language signals behind the recommendation. This makes the result easier to understand instead of presenting it as a hidden decision.

## Why it is useful

The purpose is not to replace support staff. It is to give them a faster, more consistent first step. By suggesting the right team early, the project can reduce avoidable transfers and help a customer reach the person who can solve the problem sooner.

## How we demonstrate it

During the presentation, a visitor can type a complaint or choose a sample complaint. NUT then displays the recommended route, confidence level, alternative route scores, and recognised words. The site also explains the challenge, the journey from message to route, and the responsible use of the project.

## Responsible use

This is a classroom prototype trained with fictional sample complaints. A real company deployment would need approved historical data, privacy protection, continuous testing, and human review for uncertain cases.

## Deployment status

A deployment configuration is included so the project can be hosted when the group is ready to publish it.
