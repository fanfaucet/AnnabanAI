import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';

dotenv.config();

export function authenticateJWT(req: Request, res: Response, next: NextFunction): void {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith('Bearer ') ? authHeader.split(' ')[1] : undefined;

  if (!token) {
    res.status(401).json({ status: 'error', timestamp: new Date().toISOString(), message: 'No token provided' });
    return;
  }

  const secret = process.env.JWT_SECRET;
  if (!secret) {
    res.status(500).json({ status: 'error', timestamp: new Date().toISOString(), message: 'Server misconfiguration: JWT_SECRET missing' });
    return;
  }

  jwt.verify(token, secret, (err) => {
    if (err) {
      res.status(403).json({ status: 'error', timestamp: new Date().toISOString(), message: 'Invalid token' });
      return;
    }
    next();
  });
}
