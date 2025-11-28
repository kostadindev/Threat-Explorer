import React from 'react';
import { Table, Alert } from 'antd';

interface TableRendererProps {
    content: string;
}

interface TableData {
    columns: string[];
    data: Record<string, any>[];
}

const TableRenderer: React.FC<TableRendererProps> = ({ content }) => {
    let parsedData: TableData | null = null;

    try {
        parsedData = JSON.parse(content);
    } catch (e) {
        // If parsing fails, we assume it's still streaming/loading
        // We can't easily distinguish between "invalid JSON" and "incomplete JSON" 
        // without more complex logic, but for this use case, "loading" is a safe default for the user.
        return (
            <div className="my-4 p-4 border border-gray-200 rounded-lg bg-gray-50 dark:bg-gray-800 dark:border-gray-700">
                <div className="flex items-center justify-center space-x-2 text-gray-500">
                    <span className="loading-dots">Loading table data...</span>
                </div>
            </div>
        );
    }

    if (!parsedData || !parsedData.columns || !parsedData.data) {
        // This is valid JSON but invalid structure
        return <Alert message="Error" description="Invalid table data format." type="error" showIcon />;
    }

    const columns = parsedData.columns.map((col) => ({
        title: col,
        dataIndex: col,
        key: col,
        width: 150, // Set a default width
    }));

    return (
        <div className="my-4 overflow-hidden">
            <Table
                dataSource={parsedData.data}
                columns={columns}
                pagination={{ pageSize: 5 }}
                size="small"
                rowKey={(record) => JSON.stringify(record)}
                bordered
                scroll={{ x: 'max-content' }}
            />
        </div>
    );
};

export default TableRenderer;
