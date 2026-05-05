async (page) => {
  await page.evaluate(() => localStorage.setItem("milano-guide-version", "desktop"));
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForSelector("[data-route-map-card]");

  const ids = ["day1", "day2", "day3", "day4", "day5", "day6"];
  const results = [];

  for (const id of ids) {
    const card = page.locator(`[data-route-map-card="${id}"]`);
    const button = card.locator("[data-route-map-open]");
    if ((await button.textContent())?.includes("열기")) {
      await button.click();
      await page.waitForTimeout(7000);
    }

    const path = `D:/Wedding/output/browser-check/20260504-all-route-check/${id}-route-check.png`;
    await card.locator("[data-route-map-target]").screenshot({ path });

    results.push(await card.evaluate((node, screenshotPath) => {
      const status = node.querySelector("[data-route-map-status]")?.textContent || "";
      const target = node.querySelector("[data-route-map-target]");
      const titles = Array.from(target?.querySelectorAll("[title]") || [])
        .map((el) => el.getAttribute("title"))
        .filter(Boolean);
      return {
        id: node.dataset.routeMapCard,
        status,
        screenshotPath,
        hasFallback: status.includes("보조선") || status.includes("불러오지 못"),
        hasMojibake: status.includes("�") || status.includes("??"),
        markerTitleCount: new Set(titles).size
      };
    }, path));
  }

  return results;
}
