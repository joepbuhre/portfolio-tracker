export const EuroFormatter = new Intl.NumberFormat("nl-NL", {
    style: "currency",
    currency: "EUR",
})

export const PercentageFormatter = new Intl.NumberFormat("nl-NL", {
    style: "percent",
    maximumFractionDigits: 2,
})