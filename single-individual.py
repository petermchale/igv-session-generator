#!/usr/bin/env python3
"""
Generate an IGV session XML file for a single individual with phased genomic data.
"""

import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os 

def create_igv_session(
    individual_id,
    locus,
    genome="hg38",
    base_url="http://localhost:8080",
    include_bam_tracks=True,
    methylation_type="count"
):
    """
    Create an IGV session XML for a single individual.
    
    Parameters:
    -----------
    individual_id : str
        The ID of the individual (e.g., "sample001")
    locus : str
        Initial genomic locus to display (e.g., "chr14:100826000-100827000")
    genome : str
        Reference genome (default: "hg38")
    base_url : str
        Base URL for data files (default: "http://localhost:8080")
    include_bam_tracks : bool
        Whether to include BAM tracks (default: True)
    methylation_type : str
        Type of methylation data: "model" or "count" (default: "count")
    
    Returns:
    --------
    str
        Formatted XML string for the IGV session
    """
    
    # Create root Session element
    session = ET.Element("Session", {
        "genome": genome,
        "locus": locus,
        "version": "8"
    })
    
    # Create Resources section
    resources = ET.SubElement(session, "Resources")
    
    # Add DNA methylation bigWig resources
    ET.SubElement(resources, "Resource", {
        "path": f"{base_url}/founder-phased/{individual_id}.dna-methylation.founder-phased.mat.{methylation_type}.{genome}.bw",
        "type": "bw"
    })
    ET.SubElement(resources, "Resource", {
        "path": f"{base_url}/founder-phased/{individual_id}.dna-methylation.founder-phased.pat.{methylation_type}.{genome}.bw",
        "type": "bw"
    })
    
    # Add haplotype map block BED resources with indices
    ET.SubElement(resources, "Resource", {
        "index": f"{base_url}/founder-phased/{individual_id}.hap-map-blocks.paternal.sorted.bed.gz.tbi",
        "path": f"{base_url}/founder-phased/{individual_id}.hap-map-blocks.paternal.sorted.bed.gz",
        "type": "bed"
    })
    ET.SubElement(resources, "Resource", {
        "index": f"{base_url}/founder-phased/{individual_id}.hap-map-blocks.maternal.sorted.bed.gz.tbi",
        "path": f"{base_url}/founder-phased/{individual_id}.hap-map-blocks.maternal.sorted.bed.gz",
        "type": "bed"
    })
    
    # Add BAM resources if requested
    if include_bam_tracks:
        ET.SubElement(resources, "Resource", {
            "index": f"{base_url}/read-backed-phased/{individual_id}.GRCh38.haplotagged.bam.bai",
            "path": f"{base_url}/read-backed-phased/{individual_id}.GRCh38.haplotagged.bam",
            "type": "bam"
        })
    
    # Create DataPanel with methylation tracks
    data_panel = ET.SubElement(session, "Panel", {"name": "DataPanel", "height": "200"})
    
    # Paternal methylation track
    pat_track = ET.SubElement(data_panel, "Track", {
        "attributeKey": f"{individual_id}.dna-methylation.founder-phased.pat.{methylation_type}.{genome}.bw",
        "autoScale": "false",
        "clazz": "org.broad.igv.track.DataSourceTrack",
        "fontSize": "10",
        "id": f"{base_url}/founder-phased/{individual_id}.dna-methylation.founder-phased.pat.{methylation_type}.{genome}.bw",
        "name": f"{individual_id}.dna-methylation.founder-phased.pat.{methylation_type}.{genome}.bw",
        "renderer": "BAR_CHART",
        "visible": "true",
        "windowFunction": "mean"
    })
    ET.SubElement(pat_track, "DataRange", {
        "baseline": "0.0",
        "drawBaseline": "true",
        "flipAxis": "false",
        "maximum": "1.0",
        "minimum": "0.0",
        "type": "LINEAR"
    })
    
    # Maternal methylation track
    mat_track = ET.SubElement(data_panel, "Track", {
        "attributeKey": f"{individual_id}.dna-methylation.founder-phased.mat.{methylation_type}.{genome}.bw",
        "autoScale": "false",
        "clazz": "org.broad.igv.track.DataSourceTrack",
        "fontSize": "10",
        "id": f"{base_url}/founder-phased/{individual_id}.dna-methylation.founder-phased.mat.{methylation_type}.{genome}.bw",
        "name": f"{individual_id}.dna-methylation.founder-phased.mat.{methylation_type}.{genome}.bw",
        "renderer": "BAR_CHART",
        "visible": "true",
        "windowFunction": "mean"
    })
    ET.SubElement(mat_track, "DataRange", {
        "baseline": "0.0",
        "drawBaseline": "true",
        "flipAxis": "false",
        "maximum": "1.0",
        "minimum": "0.0",
        "type": "LINEAR"
    })
    
    # Add BAM panel if requested
    if include_bam_tracks:
        bam_panel = ET.SubElement(session, "Panel", {"name": f"Panel{individual_id}_bam", "height": "400"})
        
        # Coverage track
        coverage_track = ET.SubElement(bam_panel, "Track", {
            "attributeKey": f"{individual_id}.GRCh38.haplotagged.bam Coverage",
            "autoScale": "true",
            "clazz": "org.broad.igv.sam.CoverageTrack",
            "fontSize": "10",
            "id": f"{base_url}/read-backed-phased/{individual_id}.GRCh38.haplotagged.bam_coverage",
            "name": f"{individual_id}.GRCh38.haplotagged.bam Coverage",
            "snpThreshold": "0.2",
            "visible": "true"
        })
        ET.SubElement(coverage_track, "DataRange", {
            "baseline": "0.0",
            "drawBaseline": "true",
            "flipAxis": "false",
            "minimum": "0.0",
            "type": "LINEAR"
        })
        
        # Alignment track
        alignment_track = ET.SubElement(bam_panel, "Track", {
            "attributeKey": f"{individual_id}.GRCh38.haplotagged.bam",
            "clazz": "org.broad.igv.sam.AlignmentTrack",
            "color": "185,185,185",
            "displayMode": "FULL",
            "experimentType": "THIRD_GEN",
            "fontSize": "10",
            "id": f"{base_url}/read-backed-phased/{individual_id}.GRCh38.haplotagged.bam",
            "name": f"{individual_id}.GRCh38.haplotagged.bam",
            "visible": "true"
        })
        ET.SubElement(alignment_track, "RenderOptions", {
            "basemodFilter": "m,",
            "colorOption": "BASE_MODIFICATION_2COLOR",
            "duplicatesOption": "FILTER",
            "groupByOption": "PHASE",
            "hideSmallIndels": "true",
            "shadeBasesOption": "false",
            "showMismatches": "true",
            "smallIndelThreshold": "50"
        })
    
    # Create FeaturePanel
    feature_panel = ET.SubElement(session, "Panel", {"name": "FeaturePanel", "height": "150"})
    
    # Reference sequence track
    ET.SubElement(feature_panel, "Track", {
        "attributeKey": "Reference sequence",
        "clazz": "org.broad.igv.track.SequenceTrack",
        "fontSize": "10",
        "id": "Reference sequence",
        "name": "Reference sequence",
        "sequenceTranslationStrandValue": "+",
        "shouldShowTranslation": "false",
        "visible": "true"
    })
    
    # RefSeq Select track
    ET.SubElement(feature_panel, "Track", {
        "attributeKey": "Refseq Select",
        "clazz": "org.broad.igv.track.FeatureTrack",
        "colorScale": "ContinuousColorScale;0.0;127.0;255,255,255;0,0,178",
        "fontSize": "10",
        "groupByStrand": "false",
        "id": "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/database/ncbiRefSeqSelect.txt.gz",
        "name": "Refseq Select",
        "visible": "true"
    })
    
    # Paternal haplotype blocks track
    ET.SubElement(feature_panel, "Track", {
        "attributeKey": f"{individual_id}.hap-map-blocks.paternal.sorted.bed.gz",
        "clazz": "org.broad.igv.track.FeatureTrack",
        "featureVisibilityWindow": "2147483647",
        "fontSize": "10",
        "groupByStrand": "false",
        "id": f"{base_url}/founder-phased/{individual_id}.hap-map-blocks.paternal.sorted.bed.gz",
        "name": f"{individual_id}.hap-map-blocks.paternal.sorted.bed.gz",
        "visible": "true"
    })
    
    # Maternal haplotype blocks track
    ET.SubElement(feature_panel, "Track", {
        "attributeKey": f"{individual_id}.hap-map-blocks.maternal.sorted.bed.gz",
        "clazz": "org.broad.igv.track.FeatureTrack",
        "featureVisibilityWindow": "2147483647",
        "fontSize": "10",
        "groupByStrand": "false",
        "id": f"{base_url}/founder-phased/{individual_id}.hap-map-blocks.maternal.sorted.bed.gz",
        "name": f"{individual_id}.hap-map-blocks.maternal.sorted.bed.gz",
        "visible": "true"
    })
    
    # Add PanelLayout to control relative panel heights
    # Format: comma-separated fractions representing divider positions
    # Values between 0 and 1, representing cumulative fraction of total height
    if include_bam_tracks:
        # Three panels: DataPanel (15%), BAM panel (60%), FeaturePanel (25%)
        ET.SubElement(session, "PanelLayout", {
            "dividerFractions": "0.15,0.75"
        })
    else:
        # Two panels: DataPanel (30%), FeaturePanel (70%)
        ET.SubElement(session, "PanelLayout", {
            "dividerFractions": "0.30"
        })
    
    # Convert to pretty-printed XML string
    xml_str = ET.tostring(session, encoding='unicode')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="    ")
    
    # Remove extra blank lines
    lines = [line for line in pretty_xml.split('\n') if line.strip()]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate an IGV session XML file for a single individual with phased genomic data."
    )
    
    # Required arguments
    parser.add_argument(
        "individual_id",
        type=str,
        help="The ID of the individual (e.g., '200081')"
    )
    
    parser.add_argument(
        "locus",
        type=str,
        help="Initial genomic locus to display (e.g., 'chr14:100826000-100827000')"
    )
    
    args = parser.parse_args()
    
    # Generate the session
    xml_content = create_igv_session(
        individual_id=args.individual_id,
        locus=args.locus,
    )

    # Create directory to store sessions 
    sessions_dir = 'igv-sessions'
    os.makedirs(sessions_dir, exist_ok=True)

    # Determine output file
    output_file = f"{sessions_dir}/{args.individual_id}.{args.locus}.xml"
    
    # Save the file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print(f"IGV session file created: {output_file}")

if __name__ == "__main__":
    main()