import { addHours, format, subHours, subDays } from "date-fns"

export interface TimeSeriesPoint {
    time: string
    actual: number | null
    forecast: number | null
    lowerCI: number | null
    upperCI: number | null
}

export interface Patient {
    id: string
    name: string
    age: number
    gender: "M" | "F"
    diagnosis: string
    admissionDate: string
    dischargeReadiness: number // 0-100
    readmissionRisk: number // 0-100
    status: "Stable" | "Critical" | "Discharge Ready"
}

export interface OperationalMetric {
    label: string
    value: string | number
    trend: "up" | "down" | "neutral"
    trendValue: string
    status: "normal" | "warning" | "critical"
}

// Generate Prophet-style data (History + Forecast)
export function generateOccupancyData(hoursHistory = 24, hoursForecast = 12): TimeSeriesPoint[] {
    const data: TimeSeriesPoint[] = []
    const now = new Date()
    const totalPoints = hoursHistory + hoursForecast

    let baseValue = 85 // % Occupancy base

    for (let i = 0; i < totalPoints; i++)
    {
        const time = subHours(now, hoursHistory - i)
        const isForecast = i >= hoursHistory

        // Simple seasonality simulation
        const hour = time.getHours()
        const seasonality = Math.sin((hour / 24) * Math.PI * 2) * 5
        const noise = (Math.random() - 0.5) * 3

        let actual: number | null = null
        let forecast: number | null = null
        let lowerCI: number | null = null
        let upperCI: number | null = null

        const value = Math.min(100, Math.max(0, baseValue + seasonality + noise))

        if (isForecast)
        {
            forecast = value
            // CI widens as we go further into future
            const uncertainty = (i - hoursHistory) * 0.5 + 2
            lowerCI = value - uncertainty
            upperCI = value + uncertainty
        } else
        {
            actual = value
        }

        data.push({
            time: format(time, "HH:mm"),
            actual: actual ? Number(actual.toFixed(1)) : null,
            forecast: forecast ? Number(forecast.toFixed(1)) : null,
            lowerCI: lowerCI ? Number(lowerCI.toFixed(1)) : null,
            upperCI: upperCI ? Number(upperCI.toFixed(1)) : null
        })
    }

    return data
}

export const mockPatients: Patient[] = [
    { id: "P-1024", name: "John Doe", age: 65, gender: "M", diagnosis: "Sepsis", admissionDate: "2023-10-25", dischargeReadiness: 45, readmissionRisk: 72, status: "Critical" },
    { id: "P-1025", name: "Mary Smith", age: 52, gender: "F", diagnosis: "Pneumonia", admissionDate: "2023-10-26", dischargeReadiness: 92, readmissionRisk: 15, status: "Discharge Ready" },
    { id: "P-1026", name: "Robert Johnson", age: 70, gender: "M", diagnosis: "CHF Exacerbation", admissionDate: "2023-10-27", dischargeReadiness: 60, readmissionRisk: 45, status: "Stable" },
    { id: "P-1027", name: "Emily Davis", age: 34, gender: "F", diagnosis: "Appendicitis", admissionDate: "2023-10-28", dischargeReadiness: 88, readmissionRisk: 5, status: "Discharge Ready" },
    { id: "P-1028", name: "Michael Wilson", age: 58, gender: "M", diagnosis: "COPD", admissionDate: "2023-10-25", dischargeReadiness: 30, readmissionRisk: 85, status: "Critical" },
]
