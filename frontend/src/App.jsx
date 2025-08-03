import React, { useState, useEffect } from 'react';
import { 
  Search, Download, Calendar, User, Gavel, FileText, 
  AlertCircle, CheckCircle, Clock, ExternalLink 
} from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

const App = () => {
  const [courts, setCourts] = useState([]);
  const [caseTypes, setCaseTypes] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [searchForm, setSearchForm] = useState({
    court_id: '',
    case_type_id: '',
    case_number: '',
    filing_year: new Date().getFullYear().toString()
  });
  
  const [searchResult, setSearchResult] = useState(null);
  const [activeTab, setActiveTab] = useState('search');

  // Load initial data
  useEffect(() => {
    loadCourts();
    loadSearchHistory();
  }, []);

  // Load case types when court changes
  useEffect(() => {
    if (searchForm.court_id) {
      loadCaseTypes(searchForm.court_id);
    }
  }, [searchForm.court_id]);

  const loadCourts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/courts/`);
      const data = await response.json();
      // console.log(data);
      setCourts(data.results);
    } catch (err) {
      setError('Failed to load courts');
    }
  };

  const loadCaseTypes = async (courtId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/case-types/?court_id=${courtId}`);
      const data = await response.json();
      console.log(data);  
      setCaseTypes(data.results);
    } catch (err) {
      setError('Failed to load case types');
    }
  };

  const loadSearchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/case-history/`);
      const data = await response.json();
      setSearchHistory(data.results || []);
    } catch (err) {
      console.error('Failed to load search history');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSearchForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    setSearchResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/case-search/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchForm)
      });

      const data = await response.json();

      if (data.success) {
        setSearchResult(data.data);
        setSuccess('Case details retrieved successfully!');
        loadSearchHistory(); // Refresh history
      } else {
        setError(data.error || 'Search failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = async (documentId, fileName) => {
    try {
      const response = await fetch(`${API_BASE_URL}/download-pdf/${documentId}/`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${fileName}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } else {
        setError('Failed to download PDF');
      }
    } catch (err) {
      setError('Error downloading PDF');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN');
  };

  const getStatusColor = (success) => {
    return success ? 'text-green-600' : 'text-red-600';
  };

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 10 }, (_, i) => currentYear - i);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Gavel className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                Court Data Fetcher
              </h1>
            </div>
            <div className="text-sm text-gray-500">
              eCourts India Portal
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('search')}
              className={`pb-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'search'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Search className="w-4 h-4 inline mr-2" />
              Case Search
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`pb-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Clock className="w-4 h-4 inline mr-2" />
              Search History
            </button>
          </nav>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <div className="ml-3">
                <p className="text-sm text-green-800">{success}</p>
              </div>
            </div>
          </div>
        )}

        {/* Search Tab */}
        {activeTab === 'search' && (
          <div className="space-y-8">
            {/* Search Form */}
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-6">
                Search Case Details
              </h2>
              
              <form onSubmit={handleSearch} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Court Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select Court
                    </label>
                    <select
                      name="court_id"
                      value={searchForm.court_id}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Choose a court...</option>
                      {Array.isArray(courts) && courts.map(court => (
                        <option key={court.id} value={court.id}>
                          {court.name}, {court.location}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Case Type Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Case Type
                    </label>
                    <select
                      name="case_type_id"
                      value={searchForm.case_type_id}
                      onChange={handleInputChange}
                      required
                      disabled={!searchForm.court_id}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                    >
                      <option value="">Choose case type...</option>
                      {caseTypes.map(type => (
                        <option key={type.id} value={type.id}>
                          {type.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Case Number */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Case Number
                    </label>
                    <input
                      type="text"
                      name="case_number"
                      value={searchForm.case_number}
                      onChange={handleInputChange}
                      required
                      placeholder="e.g., 123/2023"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {/* Filing Year */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Filing Year
                    </label>
                    <select
                      name="filing_year"
                      value={searchForm.filing_year}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {years.map(year => (
                        <option key={year} value={year}>
                          {year}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={loading}
                    className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Searching...
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5 mr-2" />
                        Search Case
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>

            {/* Search Results */}
            {searchResult && (
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-6">
                  Case Details
                </h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Case Information */}
                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Case Information</h3>
                    
                    <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Case Number:</span>
                        <span className="text-sm font-medium">
                          {searchResult.case_number}/{searchResult.filing_year}
                        </span>
                      </div>
                      
                      {searchResult.case_detail?.cnr_number && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">CNR Number:</span>
                          <span className="text-sm font-medium">
                            {searchResult.case_detail.cnr_number}
                          </span>
                        </div>
                      )}
                      
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Court:</span>
                        <span className="text-sm font-medium">
                          {searchResult.court_name}
                        </span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Case Type:</span>
                        <span className="text-sm font-medium">
                          {searchResult.case_type_name}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Party Details */}
                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Party Details</h3>
                    
                    <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                      {searchResult.case_detail?.petitioner_name && (
                        <div>
                          <div className="flex items-center text-sm text-gray-600 mb-1">
                            <User className="w-4 h-4 mr-1" />
                            Petitioner:
                          </div>
                          <div className="text-sm font-medium">
                            {searchResult.case_detail.petitioner_name}
                          </div>
                        </div>
                      )}
                      
                      {searchResult.case_detail?.respondent_name && (
                        <div>
                          <div className="flex items-center text-sm text-gray-600 mb-1">
                            <User className="w-4 h-4 mr-1" />
                            Respondent:
                          </div>
                          <div className="text-sm font-medium">
                            {searchResult.case_detail.respondent_name}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Case Status & Dates */}
                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Status & Dates</h3>
                    
                    <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                      {searchResult.case_detail?.case_status && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Status:</span>
                          <span className="text-sm font-medium">
                            {searchResult.case_detail.case_status}
                          </span>
                        </div>
                      )}
                      
                      {searchResult.case_detail?.filing_date && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Filing Date:</span>
                          <span className="text-sm font-medium">
                            {formatDate(searchResult.case_detail.filing_date)}
                          </span>
                        </div>
                      )}
                      
                      {searchResult.case_detail?.next_hearing_date && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Next Hearing:</span>
                          <span className="text-sm font-medium">
                            {formatDate(searchResult.case_detail.next_hearing_date)}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Judge & Court Hall */}
                  <div className="space-y-4">
                    <h3 className="font-medium text-gray-900">Court Details</h3>
                    
                    <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                      {searchResult.case_detail?.judge_name && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Judge:</span>
                          <span className="text-sm font-medium">
                            {searchResult.case_detail.judge_name}
                          </span>
                        </div>
                      )}
                      
                      {searchResult.case_detail?.court_hall && (
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Court Hall:</span>
                          <span className="text-sm font-medium">
                            {searchResult.case_detail.court_hall}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Documents */}
                {searchResult.case_detail?.documents?.length > 0 && (
                  <div className="mt-8">
                    <h3 className="font-medium text-gray-900 mb-4">
                      Orders & Judgments
                    </h3>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="space-y-3">
                        {searchResult.case_detail.documents.map((doc, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-white rounded border">
                            <div className="flex items-center space-x-3">
                              <FileText className="w-5 h-5 text-red-500" />
                              <div>
                                <div className="text-sm font-medium text-gray-900">
                                  {doc.file_name}
                                </div>
                                <div className="text-xs text-gray-500">
                                  {doc.document_type} • {formatDate(doc.document_date)}
                                </div>
                              </div>
                            </div>
                            <button
                              onClick={() => downloadPDF(doc.id, doc.file_name)}
                              className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                              <Download className="w-4 h-4 mr-1" />
                              Download
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Search History
              </h2>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Case Details
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Court
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date Searched
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {searchHistory.map((query) => (
                    <tr key={query.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {query.case_number}/{query.filing_year}
                        </div>
                        <div className="text-sm text-gray-500">
                          {query.case_type_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {query.court_name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatDate(query.queried_at)}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(query.queried_at).toLocaleTimeString('en-IN')}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          query.success 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {query.success ? 'Success' : 'Failed'}
                        </span>
                        {!query.success && query.error_message && (
                          <div className="text-xs text-red-600 mt-1">
                            {query.error_message}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        {query.success && query.case_detail && (
                          <button
                            onClick={() => {
                              setSearchResult(query);
                              setActiveTab('search');
                            }}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {searchHistory.length === 0 && (
                <div className="text-center py-12">
                  <Clock className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">
                    No search history
                  </h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Start by searching for a case above.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-gray-500">
            <p>
              Court Data Fetcher - Accessing public court records from eCourts India
            </p>
            <p className="mt-2">
              Data retrieved from official court portals. This tool is for informational purposes only.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;