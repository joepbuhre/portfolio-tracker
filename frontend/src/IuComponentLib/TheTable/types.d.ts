export type columnType = "string" | "number" | "date" | "other";

interface HeaderValues {
    name: string;
    type?: columnType;
    formatter?: Intl.NumberFormat | Intl.DateTimeFormat;
}

export interface Header {
    [columnName: string]: HeaderValues;
}
export interface Row {
    [columnName: string]: any;
}
