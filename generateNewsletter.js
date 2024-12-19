export const generateNewsletter = async (actionType, fromDate, toDate, selectedOption) => {
  const response = await fetch("http://127.0.0.1:8000/updates", {
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

  if (selectedOption === "All") {
    // If "All" is selected, return all options in formatted HTML
    const allOptions = Object.entries(result)
    .map(
        ([key, values]) =>
            `<strong>${key}</strong>:<ul>${values.map(value => `<li>${value}</li>`).join('')}</ul>`
    )
    .join('');

    return `${allOptions}`;
  } else {
    // Return specific product stream in formatted HTML
    const values = result[selectedOption] || [];
    return values.length
        ? `<strong>${selectedOption}</strong>:<ul>${values.map(value => `<li>${value}</li>`).join('')}</ul>`
        : `No data available for <strong>${selectedOption}</strong>.`;
  }
};
