export const generateMetrics = async (fromDate, toDate, selectedOption) => {
  // Fetch data from the backend
  console.log({ fromDate , toDate, selectedOption});
  const response = await fetch("http://127.0.0.1:8000/metrics", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      fromDate,
      toDate,
      selected_stream: selectedOption,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const result = await response.json();

  // Generate table rows dynamically based on the fetched data
  const tableRows = Object.entries(result)
  .map(([key, values]) => {
    const columns = values.map(value => `<td>${value}</td>`).join(''); // Convert values to table columns
    return `<tr><th style="text-align:left;"><strong>${key}</strong></th>${columns}</tr>`;
  })
  .join('');
  const columnNames = ["Total Epics", "Completed Epics", "In Progress Epics", "At Risk Epics", "Delayed Epics", "Not Started Epic", "Delivery Commit %", "Avg Epic Age",  "Avg Epic Fix Time"];


  // Construct the complete table
  const table = `
    <table border="1" style="border-collapse:collapse; width:100%;">
      <thead>
        <tr>
          <th style="text-align:left;">Product</th>
         ${columnNames.map(name => `<th>${name}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${tableRows}
      </tbody>
    </table>
  `;

  return table;
};
