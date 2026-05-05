async (page) => {
  const ids = ["day1", "day2", "day3", "day4", "day5", "day6"];
  const out = [];
  for (const id of ids) {
    const path = `D:/Wedding/output/browser-check/20260504-google-map-fix/${id}-road-connected.png`;
    await page
      .locator(`[data-route-map-card="${id}"] [data-route-map-target]`)
      .screenshot({ path });
    out.push(path);
  }
  return out;
}
