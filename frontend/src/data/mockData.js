export const mockCases = [
  { id: 1, title: 'Case A vs State', citation: '2023 PLD 123', court: 'Supreme Court', date: '2023-01-15' },
  { id: 2, title: 'Case B vs Federation', citation: '2023 PLD 456', court: 'High Court', date: '2023-02-20' },
  { id: 3, title: 'Case C vs Province', citation: '2023 PLD 789', court: 'District Court', date: '2023-03-10' },
];

export const mockJudges = [
  { id: 1, name: 'Justice Ali', court: 'Supreme Court', designation: 'Chief Justice' },
  { id: 2, name: 'Justice Bari', court: 'High Court', designation: 'Senior Judge' },
];

export const mockLawyers = [
  { id: 1, name: 'Advocate Khan', firm: 'Khan & Associates', specialization: 'Criminal Law' },
  { id: 2, name: 'Advocate Ahmed', firm: 'Ahmed Law Chambers', specialization: 'Corporate Law' },
];

export const mockStatutes = [
  { id: 1, title: 'Pakistan Penal Code', year: 1860, type: 'Act' },
  { id: 2, title: 'Code of Criminal Procedure', year: 1898, type: 'Act' },
];

export const mockJournals = [
  { id: 1, title: 'PLD 2023', volume: 1, year: 2023 },
  { id: 2, title: 'PLD 2022', volume: 2, year: 2022 },
];

export const mockClients = [
  { id: 1, name: 'Client A', email: 'a@example.com', phone: '0300-1234567', type: 'Individual' },
  { id: 2, name: 'Client B', email: 'b@example.com', phone: '0300-7654321', type: 'Corporate' },
];

export const mockRecommendations = [
  { id: 1, case_id: 1, title: 'Case A vs State', score: 95, reason: 'Similar facts and legal issues' },
  { id: 2, case_id: 2, title: 'Case B vs Federation', score: 87, reason: 'Same jurisdiction and subject matter' },
];

export const mockSearchHistory = [
  { id: 1, query: 'criminal procedure', timestamp: '2023-10-01T10:00:00Z', results_count: 45 },
  { id: 2, query: 'constitutional rights', timestamp: '2023-10-02T14:30:00Z', results_count: 32 },
];

export const mockAnalytics = {
  total_searches: 1250,
  unique_users: 340,
  avg_results: 28,
  top_queries: [
    { query: 'criminal procedure', count: 89 },
    { query: 'constitutional rights', count: 76 },
    { query: 'property law', count: 65 },
  ],
};
