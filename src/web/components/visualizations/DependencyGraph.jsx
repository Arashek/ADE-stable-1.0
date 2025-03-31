import React, { useEffect, useRef, useState } from 'react';
import styled from 'styled-components';
import * as d3 from 'd3';
import { FaSearch, FaExpand, FaCompress } from 'react-icons/fa';

const GraphContainer = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  background: ${props => props.theme.background};
  overflow: hidden;
`;

const Controls = styled.div`
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
  z-index: 10;
`;

const ControlButton = styled.button`
  padding: 8px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.buttonBackground};
  color: ${props => props.theme.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }
`;

const SearchInput = styled.input`
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.inputBackground};
  color: ${props => props.theme.text};
  width: 200px;
  margin-right: 8px;

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${props => props.theme.primary};
  }
`;

const NodeTooltip = styled.div`
  position: absolute;
  background: ${props => props.theme.cardBackground};
  border-radius: 4px;
  padding: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  z-index: 100;
  font-size: 12px;
`;

const DependencyGraph = () => {
  const svgRef = useRef(null);
  const [tooltip, setTooltip] = useState({ show: false, content: '', x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Sample data structure
  const data = {
    nodes: [
      { id: 1, name: 'Frontend', type: 'component', status: 'in_progress' },
      { id: 2, name: 'Backend', type: 'component', status: 'completed' },
      { id: 3, name: 'Database', type: 'component', status: 'completed' },
      { id: 4, name: 'API Gateway', type: 'component', status: 'in_progress' },
      { id: 5, name: 'Authentication', type: 'service', status: 'blocked' },
      { id: 6, name: 'User Management', type: 'service', status: 'in_progress' }
    ],
    links: [
      { source: 1, target: 2, type: 'depends_on' },
      { source: 2, target: 3, type: 'depends_on' },
      { source: 4, target: 2, type: 'depends_on' },
      { source: 5, target: 4, type: 'depends_on' },
      { source: 6, target: 5, type: 'depends_on' }
    ]
  };

  useEffect(() => {
    if (!svgRef.current) return;

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    // Clear previous SVG content
    d3.select(svgRef.current).selectAll('*').remove();

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create zoom behavior
    const zoomBehavior = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
        setZoom(event.transform.k);
      });

    svg.call(zoomBehavior);

    // Create main group for zooming
    const g = svg.append('g');

    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50));

    // Create arrow markers
    svg.append('defs').selectAll('marker')
      .data(['depends_on'])
      .enter().append('marker')
      .attr('id', d => d)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 15)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');

    // Create links
    const link = g.append('g')
      .selectAll('line')
      .data(data.links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 1)
      .attr('marker-end', d => `url(#${d.type})`);

    // Create nodes
    const node = g.append('g')
      .selectAll('g')
      .data(data.nodes)
      .enter().append('g')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add circles to nodes
    node.append('circle')
      .attr('r', 20)
      .attr('fill', d => {
        switch (d.status) {
          case 'completed': return '#4CAF50';
          case 'in_progress': return '#FFC107';
          case 'blocked': return '#F44336';
          default: return '#9E9E9E';
        }
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Add labels to nodes
    node.append('text')
      .attr('dy', 4)
      .attr('text-anchor', 'middle')
      .attr('fill', '#fff')
      .attr('font-size', '12px')
      .text(d => d.name);

    // Add hover effects
    node
      .on('mouseover', (event, d) => {
        setTooltip({
          show: true,
          content: `${d.name} (${d.type})`,
          x: event.pageX,
          y: event.pageY
        });
      })
      .on('mouseout', () => {
        setTooltip({ show: false, content: '', x: 0, y: 0 });
      });

    // Update positions on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, []);

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      svgRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <GraphContainer>
      <Controls>
        <SearchInput placeholder="Search nodes..." />
        <ControlButton onClick={toggleFullscreen}>
          {isFullscreen ? <FaCompress /> : <FaExpand />}
        </ControlButton>
      </Controls>

      <svg ref={svgRef} />

      {tooltip.show && (
        <NodeTooltip
          style={{
            left: tooltip.x + 10,
            top: tooltip.y + 10
          }}
        >
          {tooltip.content}
        </NodeTooltip>
      )}
    </GraphContainer>
  );
};

export default DependencyGraph; 