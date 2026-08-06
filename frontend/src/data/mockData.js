/**
 * Mock data for development and testing purposes.
 * Used when backend APIs are unavailable.
 */

export const mockCases = [
  {
    id: "1",
    title: "Constitutional Petition No. 1 of 2024",
    citation: "2024 SCMR 123",
    court: "Supreme Court of Pakistan",
    date: "2024-01-15",
    parties: "Pakistan v. Citizen's Rights Group",
    headnote: "Fundamental rights under Article 19 and freedom of expression in the digital age.",
    status: "Decided"
  },
  {
    id: "2",
    title: "Civil Appeal No. 45 of 2023",
    citation: "2023 PLC(Cs) 456",
    court: "Lahore High Court",
    date: "2023-11-20",
    parties: "ABC Corporation v. XYZ Ltd.",
    headnote: "Contractual obligations and specific performance under the Contract Act, 1872.",
    status: "Pending"
  },
  {
    id: "3",
    title: "Criminal Revision No. 12 of 2024",
    citation: "2024 PCrLJ 89",
    court: "Sindh High Court",
    date: "2024-02-10",
    parties: "State v. Muhammad Ahmed",
    headnote: "Bail considerations in non-bailable offenses under Section 497 Cr.P.C.",
    status: "Decided"
  },
  {
    id: "4",
    title: "Constitutional Petition No. 8 of 2023",
    citation: "2023 MLD 234",
    court: "Islamabad High Court",
    date: "2023-09-05",
    parties: "Employee's Union v. Ministry of Labour",
    headnote: "Labour rights and protection of workers under the Industrial Relations Act.",
    status: "Pending"
  },
  {
    id: "5",
    title: "Tax Reference No. 3 of 2024",
    citation: "2024 YLR 567",
    court: "Peshawar High Court",
    date: "2024-03-01",
    parties: "Revenue Authority v. Private Company Ltd.",
    headnote: "Interpretation of tax statutes and assessment procedures under the Income Tax Ordinance.",
    status: "Decided"
  }
];

export const mockStatutes = [
  {
    id: "1",
    title: "Constitution of the Islamic Republic of Pakistan, 1973",
    year: 1973,
    category: "Constitutional Law",
    status: "Active"
  },
  {
    id: "2",
    title: "Pakistan Penal Code, 1860",
    year: 1860,
    category: "Criminal Law",
    status: "Active"
  },
  {
    id: "3",
    title: "Code of Criminal Procedure, 1898",
    year: 1898,
    category: "Criminal Procedure",
    status: "Active"
  },
  {
    id: "4",
    title: "Contract Act, 1872",
    year: 1872,
    category: "Civil Law",
    status: "Active"
  },
  {
    id: "5",
    title: "Income Tax Ordinance, 2001",
    year: 2001,
    category: "Tax Law",
    status: "Active"
  }
];

export const mockJudges = [
  { id: "1", name: "Chief Justice of Pakistan", court: "Supreme Court", case_count: 1250 },
  { id: "2", name: "Justice Ayesha Malik", court: "Supreme Court", case_count: 890 },
  { id: "3", name: "Justice Qazi Faez Isa", court: "Supreme Court", case_count: 1100 },
  { id: "4", name: "Justice Mansoor Ali Shah", court: "Supreme Court", case_count: 950 },
  { id: "5", name: "Justice Yahya Afridi", court: "Supreme Court", case_count: 780 }
];

export const mockLawyers = [
  { id: "1", name: "Hamid Khan", case_count: 2450, specialization: "Constitutional Law" },
  { id: "2", name: "Aitzaz Ahsan", case_count: 1890, specialization: "Criminal Law" },
  { id: "3", name: "Asma Jahangir", case_count: 2100, specialization: "Human Rights" },
  { id: "4", name: "Munir A. Malik", case_count: 1560, specialization: "Corporate Law" },
  { id: "5", name: "Salman Akram Raja", case_count: 1340, specialization: "Tax Law" }
];

export const mockRecentActivity = [
  { id: "1", action: "Case viewed", description: "Viewed 2024 SCMR 123", time: "2 hours ago" },
  { id: "2", action: "Search performed", description: "Searched for 'constitutional petition'", time: "5 hours ago" },
  { id: "3", action: "Document saved", description: "Saved Pakistan Penal Code summary", time: "1 day ago" },
  { id: "4", action: "Case viewed", description: "Viewed 2023 PLC(Cs) 456", time: "2 days ago" },
  { id: "5", action: "Note added", description: "Added note to Criminal Revision No. 12", time: "3 days ago" }
];

export const mockNotifications = [
  { id: "1", title: "New Case Alert", message: "A new case matching your interest has been published.", type: "alert", read: false },
  { id: "2", title: "Statute Update", message: "The Income Tax Ordinance has been amended.", type: "update", read: false },
  { id: "3", title: "System Maintenance", message: "Scheduled maintenance on Sunday 2:00 AM.", type: "info", read: true }
];
