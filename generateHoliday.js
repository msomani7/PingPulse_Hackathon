export const generateHoliday = async (actionType, fromDate, toDate) => {
  const response = await fetch("http://127.0.0.1:8000/holidays", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      fromDate,
      toDate,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const result = await response.json();
  console.log({ fromDate });

  // Format the holidays into an HTML list
  const formattedHolidays = `
    <ul style="list-style: none; padding: 0;">
      ${result.map(holiday => `<li style="margin-bottom: 10px;">${holiday}</li>`).join('')}
    </ul>
  `;

  return formattedHolidays;
};
