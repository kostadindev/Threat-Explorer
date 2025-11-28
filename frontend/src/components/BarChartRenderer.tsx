import React from 'react';
import { Alert, theme } from 'antd';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

interface BarChartRendererProps {
    content: string;
}

interface ChartData {
    xKey: string;
    yKey: string;
    data: Record<string, any>[];
    title?: string;
}

const BarChartRenderer: React.FC<BarChartRendererProps> = ({ content }) => {
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

    if (!parsedData || !parsedData.xKey || !parsedData.yKey || !parsedData.data) {
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
                <BarChart
                    data={parsedData.data}
                    margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke={token.colorBorderSecondary} />
                    <XAxis
                        dataKey={parsedData.xKey}
                        tick={{ fill: token.colorTextSecondary }}
                    />
                    <YAxis
                        tick={{ fill: token.colorTextSecondary }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: token.colorBgContainer,
                            border: `1px solid ${token.colorBorder}`,
                            borderRadius: '4px',
                            color: token.colorText,
                        }}
                    />
                    <Legend wrapperStyle={{ color: token.colorText }} />
                    <Bar
                        dataKey={parsedData.yKey}
                        fill={token.colorPrimary}
                        radius={[8, 8, 0, 0]}
                    />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default BarChartRenderer;
