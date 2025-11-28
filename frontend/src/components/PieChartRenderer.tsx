import React from 'react';
import { Alert, theme } from 'antd';
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

interface PieChartRendererProps {
    content: string;
}

interface ChartData {
    nameKey: string;
    valueKey: string;
    data: Record<string, any>[];
    title?: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FFC658', '#FF6B9D'];

const PieChartRenderer: React.FC<PieChartRendererProps> = ({ content }) => {
    const { useToken } = theme;
    const { token } = useToken();

    let parsedData: ChartData | null = null;

    try {
        parsedData = JSON.parse(content);
    } catch (e) {
        // If parsing fails, we assume it's still streaming/loading
        return (
            <div
                className="my-4 p-4 rounded-lg"
                style={{
                    backgroundColor: token.colorBgContainer,
                    border: `1px solid ${token.colorBorder}`,
                }}
            >
                <div
                    className="flex items-center justify-center space-x-2"
                    style={{ color: token.colorTextSecondary }}
                >
                    <span className="loading-dots">Loading chart data...</span>
                </div>
            </div>
        );
    }

    if (!parsedData || !parsedData.nameKey || !parsedData.valueKey || !parsedData.data) {
        // This is valid JSON but invalid structure
        return <Alert message="Error" description="Invalid chart data format." type="error" showIcon />;
    }

    return (
        <div
            className="my-4 p-4 rounded-lg"
            style={{
                backgroundColor: token.colorBgContainer,
                border: `1px solid ${token.colorBorder}`,
            }}
        >
            {parsedData.title && (
                <h3
                    className="text-lg font-semibold mb-4"
                    style={{ color: token.colorText }}
                >
                    {parsedData.title}
                </h3>
            )}
            <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                    <Pie
                        data={parsedData.data}
                        dataKey={parsedData.valueKey}
                        nameKey={parsedData.nameKey}
                        cx="50%"
                        cy="50%"
                        outerRadius={120}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                        labelLine={{
                            stroke: token.colorTextSecondary,
                        }}
                    >
                        {parsedData.data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{
                            backgroundColor: token.colorBgContainer,
                            border: `1px solid ${token.colorBorder}`,
                            borderRadius: '4px',
                            color: token.colorText,
                        }}
                    />
                    <Legend wrapperStyle={{ color: token.colorText }} />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PieChartRenderer;
