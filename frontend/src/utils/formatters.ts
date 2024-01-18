export const EuroFormatter = new Intl.NumberFormat("nl-NL", {
    style: "currency",
    currency: "EUR",
});

export const PercentageFormatter = new Intl.NumberFormat("nl-NL", {
    style: "percent",
    maximumFractionDigits: 2,
});

export const DateFormatter = new Intl.DateTimeFormat("nl-NL", {
    month: "2-digit",
    year: "numeric",
    day: "numeric",
});
