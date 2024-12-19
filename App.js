import React, { useState } from 'react';
import { generateNewsletter } from "./generateNewsletter";
import { generateMetrics } from "./generateMetrics";
import { generateHoliday } from "./generateHoliday";
import { generateRisk } from "./generateRisk";

const DateRangeDropdownPage = () => {
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [selectedOption, setSelectedOption] = useState('All');
  const [output, setOutput] = useState('');
  const [headerText, setHeaderText] = useState('Here is the news Identians!!!');
  const [loading, setLoading] = useState(false);


  const handleGenerateNewsletter = async (actionType) => {
    setHeaderText('Here is the Team Updates Identians!!!');
    setLoading(true);
    console.log({selectedOption});
   try {
     const result = await generateNewsletter(actionType, fromDate, toDate,
         selectedOption);

     console.log({fromDate});
     setOutput(result);
   } catch(error){
     setOutput('Error fetching data');
   }finally {
      setLoading(false);
   }
  };

  const handleGenerateMetrics = async (actionType) => {
    setHeaderText('Here is the Metrics Identians!!!');
    setLoading(true);
try {
  const result = await generateMetrics(fromDate, toDate, selectedOption);
  console.log({fromDate});
  setOutput(result);
} catch (error){
  setOutput('Error fetching data');
}finally {
  setLoading(false);
}
  };

  const handleGenerateHoliday = async (actionType) => {
    setHeaderText('Here is the Holidays Identians!!!')
    setLoading(true);
    try {
      const result = await generateHoliday(actionType, fromDate, toDate,
          selectedOption);
      console.log({fromDate});
      setOutput(result);
    } catch (error){
      setOutput('Error fetching data');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRisk = async (actionType) => {
    setHeaderText('Here is the Risk/Delayed Features Identians!!!');
    setLoading(true);
    try {
      const result = await generateRisk(actionType, fromDate, toDate,
          selectedOption);
      console.log({fromDate});
      setOutput(result);
    } catch (error){
      setOutput('Error fetching data');
    } finally {
      setLoading(false);
    }
  };

  return (
      <div style={{ display: 'flex', height: '100vh' }}>
        {/* Left Side: Input Section */}
        <div
            style={{
              width: '30%',
              padding: '10px',
              backgroundColor: '#2c3e50',
              color: 'white',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
        >
          <h1 style={{textAlign: 'center'}}>Ping Pulse</h1>
          <div>
            <div style={{marginBottom: '20px'}}>
              <label>
                From:
                <input
                    type="date"
                    value={fromDate}
                    onChange={(e) => setFromDate(e.target.value)}
                    style={{
                      marginLeft: '20px',
                      padding: '5px',
                      borderRadius: '4px',
                      border: '1px solid #ccc',
                    }}
                />
              </label>
            </div>
            <div style={{marginBottom: '100px'}}>
              <label>
                To:
                <input
                    type="date"
                    value={toDate}
                    onChange={(e) => setToDate(e.target.value)}
                    style={{
                      marginLeft: '35px',
                      padding: '5px',
                      borderRadius: '4px',
                      border: '1px solid #ccc',
                    }}
                />
              </label>
            </div>
            <div style={{marginBottom: '100px'}}>
              <label>
                Product Stream:
                <select
                    value={selectedOption}
                    onChange={(e) => setSelectedOption(e.target.value)}
                    style={{
                      marginLeft: '20px',
                      padding: '5px',
                      borderRadius: '4px',
                      border: '1px solid #ccc',
                    }}
                >
                  <option value="All">All</option>
                  <option value="Identity Trust">Identity Trust</option>
                  <option value="P1AS">P1AS</option>
                  <option value="iOPS">iOPS</option>
                  <option value="MT SaaS">MT SAAS</option>
                  <option value="Software">Software</option>
                  <option value="AI / Analytics Data Platform">AI/Analytics Data
                    Platform
                  </option>
                  <option value="AIC">AIC</option>
                </select>
              </label>
            </div>
          </div>
          <div style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
            <button
                onClick={() => handleGenerateNewsletter('Newsletter')}
                style={{
                  padding: '10px',
                  borderRadius: '4px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                }}
            >
              Generate Team Updates
            </button>
            <button
                onClick={() => handleGenerateRisk('Risk')}
                style={{
                  padding: '10px',
                  borderRadius: '4px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                }}
            >
            Generate Risk/Delayed Features

            </button>
            <button
                onClick={() => handleGenerateMetrics('Metrics')}
                style={{
                  padding: '10px',
                  borderRadius: '4px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                }}

            >
              Generate Metrics
            </button>
            <button
                onClick={() => handleGenerateHoliday('Holidays')}
                style={{
                  padding: '10px',
                  borderRadius: '4px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  cursor: 'pointer',
                }}
                disabled={loading}
            >
              Generate Holidays
            </button>
          </div>
        </div>

        {/* Right Side: Output Section */}
        <div
            style={{
              width: '70%',
              padding: '20px',
              backgroundColor: '#ecf0f1',
              color: '#2c3e50',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
            }}
        >
          <h2>{headerText}</h2>
          {loading ? (
              <div
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: '200px',
                    fontSize: '18px',
                    fontWeight: 'bold',
                    color: '#3498db',
                  }}
              >
                Loading...
              </div>
          ) : (
              <pre
                  style={{
                    whiteSpace: 'pre-wrap',
                    wordWrap: 'break-word',
                    padding: '20px',
                    backgroundColor: '#fff',
                    borderRadius: '4px',
                    boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
                    width: '100%',
                    maxWidth: '600px',
                  }}
                  dangerouslySetInnerHTML={{
                    __html: output || 'Generated output will appear here.',
                  }}
              />
          )}
        </div>
      </div>
  );
};

export default DateRangeDropdownPage;
