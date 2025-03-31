import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import * as d3 from 'd3';
import { FaUsers, FaChartPie, FaExclamationTriangle } from 'react-icons/fa';

const ChartContainer = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  background: ${props => props.theme.cardBackground};
  border-radius: 8px;
  padding: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.h3`
  color: ${props => props.theme.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Controls = styled.div`
  display: flex;
  gap: 8px;
`;

const ControlButton = styled.button`
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.buttonBackground};
  color: ${props => props.theme.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }
`;

const ChartContent = styled.div`
  display: flex;
  gap: 20px;
  height: calc(100% - 60px);
`;

const PieChartContainer = styled.div`
  flex: 1;
  min-width: 300px;
`;

const BarChartContainer = styled.div`
  flex: 2;
  min-width: 400px;
`;

const Legend = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: ${props => props.theme.text};
`;

const ColorBox = styled.div`
  width: 12px;
  height: 12px;
  background: ${props => props.color};
  border-radius: 2px;
`;

const ResourceAllocationChart = () => {
  const pieChartRef = useRef(null);
  const barChartRef = useRef(null);
  const [view, setView] = useState('allocation'); // 'allocation' or 'utilization'

  // Sample data
  const data = {
    resources: [
      { name: 'Frontend Team', allocation: 35, utilization: 85, capacity: 40 },
      { name: 'Backend Team', allocation: 30, utilization: 75, capacity: 40 },
      { name: 'Design Team', allocation: 20, utilization: 60, capacity: 30 },
      { name: 'QA Team', allocation: 15, utilization: 45, capacity: 30 }
    ]
  };

  useEffect(() => {
    if (!pieChartRef.current || !barChartRef.current) return;

    // Clear previous charts
    d3.select(pieChartRef.current).selectAll('*').remove();
    d3.select(barChartRef.current).selectAll('*').remove();

    // Create pie chart
    const pieWidth = pieChartRef.current.clientWidth;
    const pieHeight = pieChartRef.current.clientHeight;
    const radius = Math.min(pieWidth, pieHeight) / 2 - 40;

    const pieSvg = d3.select(pieChartRef.current)
      .append('svg')
      .attr('width', pieWidth)
      .attr('height', pieHeight)
      .append('g')
      .attr('transform', `translate(${pieWidth / 2},${pieHeight / 2})`);

    const pie = d3.pie()
      .value(d => d.allocation)
      .sort(null);

    const arc = d3.arc()
      .innerRadius(radius * 0.6)
      .outerRadius(radius);

    const color = d3.scaleOrdinal()
      .domain(data.resources.map(d => d.name))
      .range(['#4CAF50', '#2196F3', '#FFC107', '#9C27B0']);

    const pieData = pie(data.resources);

    // Add pie segments
    pieSvg.selectAll('path')
      .data(pieData)
      .enter()
      .append('path')
      .attr('d', arc)
      .attr('fill', d => color(d.data.name))
      .attr('stroke', '#fff')
      .style('stroke-width', '2px')
      .style('opacity', 0.7);

    // Add labels
    pieSvg.selectAll('text')
      .data(pieData)
      .enter()
      .append('text')
      .attr('transform', d => `translate(${arc.centroid(d)})`)
      .attr('dy', '.35em')
      .style('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('fill', '#fff')
      .text(d => `${d.data.allocation}%`);

    // Create bar chart
    const barWidth = barChartRef.current.clientWidth;
    const barHeight = barChartRef.current.clientHeight;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };

    const barSvg = d3.select(barChartRef.current)
      .append('svg')
      .attr('width', barWidth)
      .attr('height', barHeight);

    const x = d3.scaleBand()
      .domain(data.resources.map(d => d.name))
      .range([margin.left, barWidth - margin.right])
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, 100])
      .range([barHeight - margin.bottom, margin.top]);

    // Add bars
    barSvg.selectAll('rect')
      .data(data.resources)
      .enter()
      .append('rect')
      .attr('x', d => x(d.name))
      .attr('y', d => y(view === 'allocation' ? d.allocation : d.utilization))
      .attr('width', x.bandwidth())
      .attr('height', d => barHeight - margin.bottom - y(view === 'allocation' ? d.allocation : d.utilization))
      .attr('fill', d => color(d.name))
      .style('opacity', 0.7);

    // Add axes
    barSvg.append('g')
      .attr('transform', `translate(0,${barHeight - margin.bottom})`)
      .call(d3.axisBottom(x));

    barSvg.append('g')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(y));

    // Add labels
    barSvg.append('text')
      .attr('x', barWidth / 2)
      .attr('y', barHeight - 5)
      .style('text-anchor', 'middle')
      .text('Resources');

    barSvg.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('x', -barHeight / 2)
      .attr('y', 15)
      .style('text-anchor', 'middle')
      .text(view === 'allocation' ? 'Allocation (%)' : 'Utilization (%)');

  }, [view]);

  return (
    <ChartContainer>
      <Header>
        <Title>
          <FaUsers />
          Resource Allocation
        </Title>
        <Controls>
          <ControlButton
            onClick={() => setView('allocation')}
            style={{ background: view === 'allocation' ? '#2196F3' : undefined }}
          >
            <FaChartPie /> Allocation
          </ControlButton>
          <ControlButton
            onClick={() => setView('utilization')}
            style={{ background: view === 'utilization' ? '#2196F3' : undefined }}
          >
            <FaExclamationTriangle /> Utilization
          </ControlButton>
        </Controls>
      </Header>

      <ChartContent>
        <PieChartContainer ref={pieChartRef} />
        <BarChartContainer ref={barChartRef} />
      </ChartContent>

      <Legend>
        {data.resources.map(resource => (
          <LegendItem key={resource.name}>
            <ColorBox color={d3.schemeCategory10[data.resources.indexOf(resource)]} />
            {resource.name}
          </LegendItem>
        ))}
      </Legend>
    </ChartContainer>
  );
};

export default ResourceAllocationChart; 