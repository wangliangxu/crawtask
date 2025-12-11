from fastapi import APIRouter, Depends, HTTPException
import os
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.node import Node
from ..schemas.node import NodeCreate, NodeResponse, NodeUpdate
from ..security import encrypt_password

router = APIRouter(
    prefix="/api/nodes",
    tags=["nodes"],
)

from ..services.ssh_service import ssh_manager

@router.post("/test-connection")
async def test_connection(node: NodeCreate, db: Session = Depends(get_db)):
    # Create a temporary Node object (not saved to DB)
    ssh_key_path = node.ssh_key_path
    encrypted_pwd = None

    if node.password:
        encrypted_pwd = encrypt_password(node.password)


    temp_node = Node(
        name=node.name,
        host=node.host,
        port=node.port,
        username=node.username,
        encrypted_password=encrypted_pwd,
        ssh_key_path=ssh_key_path,
        is_center=1 if node.is_center else 0
    )
    
    gateway_node = None
    if not temp_node.is_center:
        # Find if there is a center node
        center_node = db.query(Node).filter(Node.is_center == 1).first()
        if center_node:
            print(f"DEBUG: Found center node {center_node.host} (ID: {center_node.id})")
            gateway_node = center_node
            
            # Fallback: If target node has no credentials, try using gateway's credentials
            if not temp_node.ssh_key_path and not temp_node.encrypted_password:
               print("DEBUG: Target node has no credentials, using gateway credentials.")
               temp_node.ssh_key_path = gateway_node.ssh_key_path
               temp_node.encrypted_password = gateway_node.encrypted_password
        else:
            print("DEBUG: No center node found in DB")
    else:
        print("DEBUG: Testing connection to center node (direct)")

    try:
        await ssh_manager.test_connection(temp_node, gateway_node=gateway_node)
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@router.post("/{node_id}/test-connection")
async def test_existing_node_connection(node_id: int, db: Session = Depends(get_db)):
    target_node = db.query(Node).filter(Node.id == node_id).first()
    if not target_node:
        raise HTTPException(status_code=404, detail="Node not found")

    gateway_node = None
    if not target_node.is_center:
        # Find if there is a center node
        center_node = db.query(Node).filter(Node.is_center == 1).first()
        if center_node:
            print(f"DEBUG: Found center node {center_node.host} (ID: {center_node.id})")
            gateway_node = center_node
            
            # Fallback: If target node has no credentials, try using gateway's credentials
            # Note: This logic is implicitly handled in ssh_service but we can be explicit if needed.
            # However, ssh_service._create_client_connection handles this fallback logic if gateway_node is passed.
    else:
        print("DEBUG: Testing connection to center node (direct)")

    try:
        await ssh_manager.test_connection(target_node, gateway_node=gateway_node)
        return {"status": "success", "message": "Connection successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@router.post("/", response_model=NodeResponse)
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    if node.is_center:
        # Demote existing center node if any
        existing_center = db.query(Node).filter(Node.is_center == 1).first()
        if existing_center:
            existing_center.is_center = 0
            db.add(existing_center)

    db_node = db.query(Node).filter(Node.name == node.name).first()
    if db_node:
        raise HTTPException(status_code=400, detail="Node name already registered")
    
    ssh_key_path = node.ssh_key_path
    encrypted_pwd = None

    if node.password:
        encrypted_pwd = encrypt_password(node.password)


    new_node = Node(
        name=node.name,
        host=node.host,
        port=node.port,
        username=node.username,
        encrypted_password=encrypted_pwd,
        ssh_key_path=ssh_key_path,
        is_center=1 if node.is_center else 0
    )
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node

@router.get("/", response_model=List[NodeResponse])
def read_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    nodes = db.query(Node).offset(skip).limit(limit).all()
    return nodes

@router.get("/{node_id}", response_model=NodeResponse)
def read_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.put("/{node_id}", response_model=NodeResponse)
def update_node(node_id: int, node_in: NodeUpdate, db: Session = Depends(get_db)):
    db_node = db.query(Node).filter(Node.id == node_id).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Check name uniqueness if changed
    if node_in.name != db_node.name:
         existing_name = db.query(Node).filter(Node.name == node_in.name).first()
         if existing_name:
             raise HTTPException(status_code=400, detail="Node name already registered")

    if node_in.is_center and not db_node.is_center:
        # Demote existing center node if any (excluding self which is already checked)
        existing_center = db.query(Node).filter(Node.is_center == 1).first()
        if existing_center:
            existing_center.is_center = 0
            db.add(existing_center)

    # Update fields
    for field, value in node_in.dict(exclude_unset=True).items():
        if field == "password":
            if value: # Only update password if provided
                db_node.encrypted_password = encrypt_password(value)
        elif field == "is_center":
             db_node.is_center = 1 if value else 0
        else:
            setattr(db_node, field, value)

    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

@router.delete("/{node_id}")
def delete_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.id == node_id).first()
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(node)
    db.commit()
    return {"ok": True}
